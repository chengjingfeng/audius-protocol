from sqlalchemy import func, desc

from src import exceptions
from src.models import User, Playlist, Repost, RepostType, Follow
from src.utils import helpers
from src.utils.db_session import get_db_read_replica
from src.queries import response_name_constants
from src.queries.query_helpers import populate_user_metadata, add_query_pagination


def get_reposters_for_playlist(args):
    user_results = []
    current_user_id = args.get('current_user_id')
    repost_playlist_id = args.get('repost_playlist_id')
    limit = args.get('limit')
    offset = args.get('offset')

    db = get_db_read_replica()
    with db.scoped_session() as session:
        # Ensure Playlist exists for provided repost_playlist_id.
        playlist_entry = session.query(Playlist).filter(
            Playlist.playlist_id == repost_playlist_id,
            Playlist.is_current == True
        ).first()
        if playlist_entry is None:
            raise exceptions.NotFoundError('Resource not found for provided playlist id')

        # Subquery to get all (user_id, follower_count) entries from Follows table.
        follower_count_subquery = (
            session.query(
                Follow.followee_user_id,
                func.count(Follow.followee_user_id).label(
                    response_name_constants.follower_count)
            )
            .filter(
                Follow.is_current == True,
                Follow.is_delete == False
            )
            .group_by(Follow.followee_user_id)
            .subquery()
        )

        # Get all Users that reposted Playlist, ordered by follower_count desc & paginated.
        query = (
            session.query(User)
            # Left outer join to associate users with their follower count.
            .outerjoin(follower_count_subquery, follower_count_subquery.c.followee_user_id == User.user_id)
            .filter(
                User.is_current == True,
                # Only select users that reposted given playlist.
                User.user_id.in_(
                    session.query(Repost.user_id)
                    .filter(
                        Repost.repost_item_id == repost_playlist_id,
                        # Select Reposts for Playlists and Albums (i.e. not Tracks).
                        Repost.repost_type != RepostType.track,
                        Repost.is_current == True,
                        Repost.is_delete == False
                    )
                )
            )
            .order_by(desc(response_name_constants.follower_count))
        )
        user_results = add_query_pagination(query, limit, offset).all()

        # Fix format to return only Users objects with follower_count field.
        if user_results:
            user_results = helpers.query_result_to_list(user_results)
            # bundle peripheral info into user results
            user_ids = [user['user_id'] for user in user_results]
            user_results = populate_user_metadata(
                session, user_ids, user_results, current_user_id)

    return user_results
