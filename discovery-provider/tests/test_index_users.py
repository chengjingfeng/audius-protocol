from datetime import datetime
from src.models import AssociatedWallet
from src.tasks.users import lookup_user_record, parse_user_event
from src.utils.db_session import get_db
from src.utils.user_event_constants import user_event_types_lookup
from src.utils import helpers
from tests.index_helpers import AttrDict, IPFSClient, Web3, UpdateTask

def get_add_user_event():
    event_type = user_event_types_lookup['add_user']
    add_user_event = AttrDict({
        '_userId': 1,
        '_handle': b'joe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
        '_wallet': '0x82Fc85A842c9922A9Db9091Cf6573754Cd2D0F14'
    })
    return event_type, AttrDict({"blockHash": "0x", "args": add_user_event})

def get_update_bio_event():
    event_type = user_event_types_lookup['update_bio']
    update_bio_event = AttrDict({
        '_userId': 1,
        '_bio': 'change description'
    })
    return event_type, AttrDict({"blockHash": "0x", "args": update_bio_event})

def get_update_multihash_event():
    event_type = user_event_types_lookup['update_multihash']
    update_multihash_event = AttrDict({
        '_userId': 1,
        '_multihashDigest': b'\x94uU\x06@\xa2\x93\xf1$d:\xe8m|rj\x02y\x93\xdf\x9bf?\xe7h\xb3y\xa6\x19\x0c\x81\xb0'
    })
    return event_type, AttrDict({"blockHash": "0x", "args": update_multihash_event})

def get_update_location_event():
    event_type = user_event_types_lookup['update_location']
    update_location_event = AttrDict({
        '_userId': 1,
        '_location':
        b'location\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    })
    return event_type, AttrDict({"blockHash": "0x", "args": update_location_event})

def get_update_profile_photo_event():
    event_type = user_event_types_lookup['update_profile_photo']
    update_profile_photo_event = AttrDict({
        '_userId': 1,
        '_profilePhotoDigest':
        b'\xc6\x0f\xc2@\x8f\xd1\xb7R\xbb\xe3\xf6\xc3\xa45\x19\x9d\xc6\x10g\x8dm\xe4\x15\x86|\x91\\r\xaa\x01\xab-'
    })
    return event_type, AttrDict({"blockHash": "0x", "args": update_profile_photo_event})

def get_update_cover_photo_event():
    event_type = user_event_types_lookup['update_cover_photo']
    update_cover_photo_event = AttrDict({
        '_userId': 1,
        '_coverPhotoDigest':
        b'C\x9a\r\xa5PO\x99\x8c\xdf;\x8cT\xdc\x18\xf5**\x80\x01\xe3j-\xd7\x11_\x84\xde%T\xd0\xcd\xc6'
    })
    return event_type, AttrDict({"blockHash": "0x", "args": update_cover_photo_event})

def get_update_name_event():
    event_type = user_event_types_lookup['update_name']
    update_name_event = AttrDict({
        '_userId': 1,
        '_name':
        b'joey\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' +
        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    })
    return event_type, AttrDict({"blockHash": "0x", "args": update_name_event})

def get_update_is_creator_event():
    event_type = user_event_types_lookup['update_is_creator']
    update_is_creator_event = AttrDict({
        '_userId': 1,
        '_isCreator': True
    })
    return event_type, AttrDict({"blockHash": "0x", "args": update_is_creator_event})

def get_update_creator_node_endpoint_event():
    event_type = user_event_types_lookup['update_creator_node_endpoint']
    update_creator_node_endpoint_event = AttrDict({
        '_userId': 1,
        '_creatorNodeEndpoint':
        'http://cn2_creator-node_1:4001,http://cn1_creator-node_1:4000,http://cn3_creator-node_1:4002'
    })
    return event_type, AttrDict({"blockHash": "0x", "args": update_creator_node_endpoint_event})

# 'update_is_verified': 'UpdateIsVerified',
multihash = helpers.multihash_digest_to_cid(
    b'\x94uU\x06@\xa2\x93\xf1$d:\xe8m|rj\x02y' +
    b'\x93\xdf\x9bf?\xe7h\xb3y\xa6\x19\x0c\x81\xb0'
)

ipfs_client = IPFSClient({
    multihash: {
        "is_creator": True,
        "is_verified": False,
        "name": "raymont",
        "handle": "rayjacobson",
        "profile_picture": None,
        "profile_picture_sizes": "Qmdad2B9JPnJ9duZgfD5mVNDwKZUTNoqZp8xdDB9bmcewk",
        "cover_photo": None,
        "cover_photo_sizes": "QmQnJ8uXf886crAticzPGgrfqxq68kAxBXXcK73geFakUo",
        "bio": "ðŸŒ\n;",
        "location": "chik fil yay!",
        "creator_node_endpoint":
        "https://creatornode2.audius.co,https://creatornode.audius.co,https://content-node.audius.co",
        "associated_wallets": {
            "0xEfFe2E2Dfc7945ED6Fd4C07c0B668589C52819BF": {
                "signature":
                "0xdde72a90dad4a0027ca87630a2b5615240d9ad545f2fc50e24952a2b4f2c5a" +
                "f76c96b9e06df5801d3e3374e247b799ac3e6dfd22b4df117fe1d6190789c5bb781b"
            },
            "0x0aDd827a4d1ad41c4D4612B4f1Df84b9d9654782": {
                "signature":
                "0xd13fc25e87dac94ba95af9e352111816aa25c1dc7ff48437660e2350a4f7a6f" +
                "413011759fa6980ba5f55b0fc66d55122afd5497b5795992cf6749bbe06553abc1b"
            }
        },
        "collectibles": {
            "73:::0x417cf58dc18edd17025689d13af2b85f403e130c": {},
            "order": ["73:::0x417cf58dc18edd17025689d13af2b85f403e130c"]
        },
        "playlist_library": {
            "contents": [
                {
                    "type": "folder",
                    "name": "my favorite playlists",
                    "contents": [
                        { "type": "playlist", "playlist_id": 500 },
                        { "type": "explore_playlist", "playlist_id": "heavy-rotation" }
                    ]
                },
                { "type": "playlist", "playlist_id": 501 },
                { "type": "playlist", "playlist_id": 502 },
                { "type": "explore_playlist", "playlist_id": "feeling-lucky" },
                { "type": "playlist", "playlist_id": 503 },
            ]
        },
        "user_id": 1
    }
})
web3 = Web3()

def test_index_users(app):
    """Tests that users are indexed correctly"""
    with app.app_context():
        db = get_db()

    update_task = UpdateTask(ipfs_client, web3)

    with db.scoped_session() as session:
        # ================== Test Add User Event ==================
        event_type, entry = get_add_user_event()

        block_number = 1
        block_timestamp = 1585336422

        # Some sqlalchemy user instance
        user_record = lookup_user_record(
            update_task,
            session,
            entry,
            block_number,
            block_timestamp,
            '0x' # txhash
        )

        assert user_record.updated_at == None

        # Fields set to None by default
        assert user_record.handle == None
        assert user_record.handle_lc == None
        assert user_record.wallet == None

        parse_user_event(
            None, # self - not used
            None, # user_contract - not used
            update_task, # only need the ipfs client for get_metadata
            session,
            None, # tx_receipt - not used
            block_number, # not used
            entry, # Contains the event args used for updating
            event_type, # String that should one of user_event_types_lookup
            user_record, # User ORM instance
            block_timestamp # Used to update the user.updated_at field
        )

        # updated_at should be updated every parse_user_event
        assert user_record.updated_at == datetime.utcfromtimestamp(block_timestamp)

        # add_user should be updated fields: handle, handle_lc, wallet
        assert user_record.handle == helpers.bytes32_to_str(entry.args._handle)
        assert user_record.handle_lc == helpers.bytes32_to_str(entry.args._handle).lower()
        assert user_record.wallet == entry.args._wallet.lower()

        # ================== Test Update User Bio Event ==================
        event_type, entry = get_update_bio_event()

        assert user_record.bio == None
        assert user_record.handle != None

        parse_user_event(
            None, # self - not used
            None, # user_contract - not used
            update_task, # only need the ipfs client for get_metadata
            session,
            None, # tx_receipt - not used
            block_number, # not used
            entry, # Contains the event args used for updating
            event_type, # String that should one of user_event_types_lookup
            user_record, # User ORM instance
            block_timestamp # Used to update the user.updated_at field
        )

        # add_user should be updated fields: handle, handle_lc, wallet
        assert user_record.bio == entry.args._bio

        # ================== Test Update User Location Event ==================
        event_type, entry = get_update_location_event()

        # `location` field is none by default
        assert user_record.location == None

        parse_user_event(
            None, # self - not used
            None, # user_contract - not used
            update_task, # only need the ipfs client for get_metadata
            session,
            None, # tx_receipt - not used
            block_number, # not used
            entry, # Contains the event args used for updating
            event_type, # String that should one of user_event_types_lookup
            user_record, # User ORM instance
            block_timestamp # Used to update the user.updated_at field
        )

        # add_user should be updated fields: handle, handle_lc, wallet
        assert user_record.location == helpers.bytes32_to_str(entry.args._location)

        # ================== Test Update User is Creator Event ==================
        event_type, entry = get_update_is_creator_event()

        # `is_creator` field is none by default
        assert user_record.is_creator == None

        parse_user_event(
            None, # self - not used
            None, # user_contract - not used
            update_task, # only need the ipfs client for get_metadata
            session,
            None, # tx_receipt - not used
            block_number, # not used
            entry, # Contains the event args used for updating
            event_type, # String that should one of user_event_types_lookup
            user_record, # User ORM instance
            block_timestamp # Used to update the user.updated_at field
        )

        # add_user should be updated fields: handle, handle_lc, wallet
        assert user_record.is_creator == entry.args._isCreator

        # ================== Test Update User Name Event ==================
        event_type, entry = get_update_name_event()

        # `name` field is none by default
        assert user_record.name == None

        parse_user_event(
            None, # self - not used
            None, # user_contract - not used
            update_task, # only need the ipfs client for get_metadata
            session,
            None, # tx_receipt - not used
            block_number, # not used
            entry, # Contains the event args used for updating
            event_type, # String that should one of user_event_types_lookup
            user_record, # User ORM instance
            block_timestamp # Used to update the user.updated_at field
        )

        # add_user should be updated fields: handle, handle_lc, wallet
        assert user_record.name == helpers.bytes32_to_str(entry.args._name)


        # ================== Test Update User CNodes Event for legacy ==================
        event_type, entry = get_update_creator_node_endpoint_event()

        # `creator_node_endpoint` field is none by default
        assert user_record.creator_node_endpoint == None

        # Set primary id so that creator node endpoints is not set
        assert user_record.primary_id == None
        user_record.primary_id = 1

        parse_user_event(
            None, # self - not used
            None, # user_contract - not used
            update_task, # only need the ipfs client for get_metadata
            session,
            None, # tx_receipt - not used
            block_number, # not used
            entry, # Contains the event args used for updating
            event_type, # String that should one of user_event_types_lookup
            user_record, # User ORM instance
            block_timestamp # Used to update the user.updated_at field
        )

        # add_user should be updated fields: handle, handle_lc, wallet
        assert user_record.creator_node_endpoint == None

        # Set primary id back to none
        user_record.primary_id = None

        # ================== Test Update User CNodes Event ==================
        event_type, entry = get_update_creator_node_endpoint_event()

        # `creator_node_endpoint` field is none by default
        assert user_record.creator_node_endpoint == None

        parse_user_event(
            None, # self - not used
            None, # user_contract - not used
            update_task, # only need the ipfs client for get_metadata
            session,
            None, # tx_receipt - not used
            block_number, # not used
            entry, # Contains the event args used for updating
            event_type, # String that should one of user_event_types_lookup
            user_record, # User ORM instance
            block_timestamp # Used to update the user.updated_at field
        )

        # add_user should be updated fields: handle, handle_lc, wallet
        assert user_record.creator_node_endpoint == entry.args._creatorNodeEndpoint

        # ================== Test Update User Profile Photo Event ==================
        event_type, entry = get_update_profile_photo_event()

        # `profile_picture` field is none by default
        assert user_record.profile_picture == None
        assert user_record.profile_picture_sizes == None

        parse_user_event(
            None, # self - not used
            None, # user_contract - not used
            update_task, # only need the ipfs client for get_metadata
            session,
            None, # tx_receipt - not used
            block_number, # not used
            entry, # Contains the event args used for updating
            event_type, # String that should one of user_event_types_lookup
            user_record, # User ORM instance
            block_timestamp # Used to update the user.updated_at field
        )

        # add_user should be updated fields: profile_picture_sizes, profile_picture
        assert user_record.profile_picture_sizes == helpers.multihash_digest_to_cid(entry.args._profilePhotoDigest)
        assert user_record.profile_picture == None

        # ================== Test Update User Cover Photo Event ==================
        event_type, entry = get_update_cover_photo_event()

        # `cover_photo` field is none by default
        assert user_record.cover_photo == None
        assert user_record.cover_photo_sizes == None

        parse_user_event(
            None, # self - not used
            None, # user_contract - not used
            update_task, # only need the ipfs client for get_metadata
            session,
            None, # tx_receipt - not used
            block_number, # not used
            entry, # Contains the event args used for updating
            event_type, # String that should one of user_event_types_lookup
            user_record, # User ORM instance
            block_timestamp # Used to update the user.updated_at field
        )

        # add_user should be updated fields: cover_photo, cover_photo_sizes
        assert user_record.cover_photo == None
        assert user_record.cover_photo_sizes == helpers.multihash_digest_to_cid(entry.args._coverPhotoDigest)

        # ================== Test Update User Metadata Event ==================
        event_type, entry = get_update_multihash_event()

        parse_user_event(
            None, # self - not used
            None, # user_contract - not used
            update_task, # only need the ipfs client for get_metadata
            session,
            None, # tx_receipt - not used
            block_number, # not used
            entry, # Contains the event args used for updating
            event_type, # String that should one of user_event_types_lookup
            user_record, # User ORM instance
            block_timestamp # Used to update the user.updated_at field
        )

        entry_multihash = helpers.multihash_digest_to_cid(entry.args._multihashDigest)
        ipfs_metadata = update_task.ipfs_client.get_metadata(entry_multihash, '', '')

        assert user_record.profile_picture == ipfs_metadata["profile_picture"]
        assert user_record.cover_photo == ipfs_metadata["cover_photo"]
        assert user_record.bio == ipfs_metadata["bio"]
        assert user_record.name == ipfs_metadata["name"]
        assert user_record.location == ipfs_metadata["location"]
        assert user_record.profile_picture_sizes == ipfs_metadata["profile_picture_sizes"]
        assert user_record.cover_photo_sizes == ipfs_metadata["cover_photo_sizes"]
        assert user_record.has_collectibles == True
        assert user_record.playlist_library == ipfs_metadata["playlist_library"]

        ipfs_associated_wallets = ipfs_metadata['associated_wallets']
        associated_wallets = session.query(AssociatedWallet).filter_by(
            user_id=user_record.user_id,
            is_current=True,
            is_delete=False
        ).all()
        for wallet in associated_wallets:
            assert wallet in ipfs_associated_wallets
