const axios = require('axios')
const fs = require('fs')

const AudiusLibs = require('../src/index')
const Web3 = require('../src/web3')
const Util = require('../src/utils')
const CreatorNode = require('../src/services/creatorNode')

const CONTENT_NODE_TYPE = 'content-node'

// PROD
// const ETH_PROVIDER_URL = 'https://eth.audius.co'
// const DISCOVERY_NODE_ENDPOINT = 'https://discoveryprovider.audius.co'
// const USER_METADATA_ENDPOINT = 'https://usermetadata.audius.co/'
// const ETH_REGISTRY_ADDRESS = '0xd976d3b4f4e22a238c1A736b6612D22f17b6f64C'
// const ETH_TOKEN_ADDRESS = '0x18aAA7115705e8be94bfFEBDE57Af9BFc265B998'
// const ETH_OWNER_WALLET = '0xC7310a03e930DD659E15305ed7e1F5Df0F0426C5'

// STAGING
// const ETH_PROVIDER_URL = 'https://eth.staging.audius.co'
// const DISCOVERY_NODE_ENDPOINT = 'https://discoveryprovider.staging.audius.co'
// const ETH_REGISTRY_ADDRESS = '0xe39b1cA04fc06c416c4eaBd188Cb1330b8FED781'
// const ETH_TOKEN_ADDRESS = '0x74f24429ec3708fc21381e017194A5711E93B751'
// const ETH_OWNER_WALLET = '0xcccc7428648c4AdC0ae262D3547584dDAE25c465'

// NOTE: Migrate URSM first via `node setup.js run user-replica-set-manager up`

// LOCAL
const ethContractsConfig = require('../eth-contracts/config.json')
const dataContractsConfig = require('../data-contracts/config.json')
const ETH_PROVIDER_ENDPOINT = 'http://localhost:8546'
const DISCOVERY_NODE_ENDPOINT = 'http://localhost:5000'
const DATA_CONTRACTS_PROVIDER_ENDPOINT = 'http://localhost:8545'
const USER_METADATA_ENDPOINT = 'http://cn-um_creator-node_1:4099'
const ETH_REGISTRY_ADDRESS = ethContractsConfig.registryAddress
const ETH_TOKEN_ADDRESS = ethContractsConfig.audiusTokenAddress
const ETH_OWNER_WALLET = ethContractsConfig.ownerWallet
const DATA_CONTRACTS_REGISTRY_ADDRESS = dataContractsConfig.registryAddress
const URSM_WALLET = dataContractsConfig.allWallets[9] // 9th index as according to URSM logic in local.js

const NUM_USERS_PER_BATCH_REQUEST = 500
const SYNC_WAIT_TIME = 60000 /* 1 min */

const configureAndInitLibs = async () => {
  const dataWeb3 = new Web3(new Web3.providers.HttpProvider(DATA_CONTRACTS_PROVIDER_ENDPOINT))

  const audiusLibsConfig = {
    ethWeb3Config: AudiusLibs.configEthWeb3(
      ETH_TOKEN_ADDRESS,
      ETH_REGISTRY_ADDRESS,
      ETH_PROVIDER_ENDPOINT,
      ETH_OWNER_WALLET
    ),
    web3Config: AudiusLibs.configExternalWeb3(
      DATA_CONTRACTS_REGISTRY_ADDRESS,
      dataWeb3,
      null /* networkId */,
      URSM_WALLET
    ),
    creatorNodeConfig: AudiusLibs.configCreatorNode(USER_METADATA_ENDPOINT),
    discoveryProviderConfig: AudiusLibs.configDiscoveryProvider(new Set([DISCOVERY_NODE_ENDPOINT])),
    isServer: true
  }

  let audiusLibs = new AudiusLibs(audiusLibsConfig)

  try {
    await audiusLibs.init()
  } catch (e) {
    if (e.message.includes('socket hang up')) {
      await Util.wait(500)
      console.log('socket hung up during libs init.. retrying')
      return configureAndInitLibs()
    } else {
      console.error(`Couldn't init libs`, e)
      throw e
    }
  }

  return audiusLibs
}

const performHealthCheck = async spInfo => {
  const endpoint = spInfo[1].endpoint
  const id = spInfo[0]
  try {
    await axios({
      method: 'get',
      url: '/health_check',
      baseURL: endpoint
    })

    return { id, endpoint, status: 200 }
  } catch (e) {
    if (e.message.includes('socket hang up')) {
      await Util.wait(500)
      console.log('socket hung up during health check.. retrying')
      return performHealthCheck(spInfo)
    } else {
      console.warn(`Could not perform health check for spId=${id},endpoint=${endpoint}:`, e.message)
    }
  }

  return { id, endpoint, status: 500 }
}

const writeDataToFile = (spIdToEndpointAndCount, userIdToRSet) => {
  fs.writeFile('computeRSet_Data.txt', `\n<userIds - replica sets>:\n` + JSON.stringify(userIdToRSet), err => {
    if (err) console.error(`Error with writing <userIds - replica sets> data:`, err)
    else console.log('Saved <userIds - replica sets> data')
  })
  fs.appendFile('computeRSet_Data.txt', '\n<service providers - number of times selected as secondary>:\n' + JSON.stringify(spIdToEndpointAndCount), err => {
    if (err) console.error(`Error with writing <service providers - number of times selected as secondary> data:`, err)
    else console.log('Saved <service providers - number of times selected as secondary> data')
  })
}

const syncSecondary = async ({ primary, secondary, wallet }) => {
  try {
    await axios({
      baseURL: secondary,
      url: '/sync',
      method: 'post',
      data: {
        wallet: [wallet],
        creator_node_endpoint: primary,
        immediate: false /* whether or not this is a blocking request and handled right away */
      }
    })
  } catch (e) {
    console.error(`Could not sync from primary=${primary} to secondary=${secondary} for wallet=${wallet}`, e)
  }
}

const getClockValue = async ({ id, endpoint, wallet, timeout = 5000 }) => {
  try {
    const clockValue = await CreatorNode.getClockValue(endpoint, wallet, timeout)
    return { clockValue, id, endpoint, wallet }
  } catch (e) {
    console.error(`Could not fetch clock value for wallet=${wallet} from endpoint=${endpoint}`, e.message)
    return { clockValue: null, id, endpoint, wallet }
  }
}

const setReplicaSet = async ({
  audiusLibs,
  primarySpId,
  secondary1SpId,
  secondary2SpId,
  userId
}) => {
  // // Update local libs state with new CN primary
  // await audiusLibs.creatorNode.setEndpoint(USER_METADATA_ENDPOINT)

  // // Write MD file with updated endpoints to db
  // // Update user creator_node_endpoint on chain if applicable
  // const oldMetadata = audiusLibs.userStateManager.getCurrentUser()
  // const newCreatorNodeEndpoint = CreatorNode.buildEndpoint(
  //   USER_METADATA_ENDPOINT, secondaries
  // )
  // const newMetadata = { ...oldMetadata,
  //   creator_node_endpoint: newCreatorNodeEndpoint
  // }
  // await audiusLibs.User.updateAndUploadMetadata({ newMetadata, userId })

  // // Ensure DN has indexed creator_node_endpoint change
  // // TODO: might not be the same after URSM migration?

  // Update in new contract
  let tx = await audiusLibs.contracts.UserReplicaSetManagerClient.updateReplicaSet(
    userId,
    primarySpId,
    [secondary1SpId, secondary2SpId]
  )

  console.log('tx for updating rset', tx)

  // await audiusLibs.User.waitForCreatorNodeEndpointIndexing(userId, newCreatorNodeEndpoint)
}

let start
const run = async () => {
  // Set up libs
  start = Date.now()
  const audiusLibs = await configureAndInitLibs()

  // Get all users that do not have a replica set assigned
  const numOfUsers = (await axios({
    method: 'get',
    url: '/latest/user',
    baseURL: DISCOVERY_NODE_ENDPOINT
  })).data.data

  console.log(`There are ${numOfUsers} users on Audius\n`)

  // Batch DP /users calls
  let userIdToWallet = {}
  let i
  for (i = 0; i <= numOfUsers; i = i + NUM_USERS_PER_BATCH_REQUEST) {
    console.log(`Processing users batch range ${i} to ${i + NUM_USERS_PER_BATCH_REQUEST}...`)
    try {
      const subsetUsers = (await axios({
        method: 'get',
        url: '/users',
        baseURL: DISCOVERY_NODE_ENDPOINT,
        params: { limit: NUM_USERS_PER_BATCH_REQUEST, offset: i }
      })).data.data

      subsetUsers
      // Filter to users that do not have a CNE
        .filter(user => !user.creator_node_endpoint)
        .forEach(user => {
        // Add userId - wallet mapping
          userIdToWallet[user.user_id] = user.wallet
        })
    } catch (e) {
      if (e.message.includes('socket hang up')) {
        await Util.wait(500)
        console.log('socket hung up.. retrying')
        i -= NUM_USERS_PER_BATCH_REQUEST
      } else {
        console.error(`Could not get users`, e)
        throw e
      }
    }
  }

  let userIds = Object.keys(userIdToWallet)
  console.log(`\n${userIds.length} users have no replica sets\nThis is ${userIds.length * 100 / numOfUsers}% of user base`)

  // Get all non-Audius SPs
  // const audiusInfraSpIdsArr = [1, 2, 3, 4/*, umID*/] // TODO: uncomment later
  const audiusInfraSpIdsArr = []
  const audiusInfraSpIds = new Set(audiusInfraSpIdsArr) // when UM is registered, exclude it as secondary
  let spIdToEndpointAndCount = {}

  const sps = await audiusLibs.ethContracts.getServiceProviderList(CONTENT_NODE_TYPE)
  sps
    .filter(sp => !audiusInfraSpIds.has(sp.spID))
    .forEach(sp => {
      spIdToEndpointAndCount[sp.spID] = { endpoint: sp.endpoint, selected: 0 }
    })
    // .map(sp => { return { id: sp.spID, endpoint: sp.endpoint } })

  console.log('spIds', spIdToEndpointAndCount)

  // Do health check for all non-Audius SPs
  const healthCheckedSPs = await Promise.all(
    Object.entries(spIdToEndpointAndCount)
      .map(entry => performHealthCheck(entry))
  )

  console.log('Health check responses:', healthCheckedSPs)

  // Filter out unhealthy nodes and retrieve id of each healthy node
  const spIds = healthCheckedSPs
    .filter(response => response.status === 200)
    .map(response => parseInt(response.id))

  // Compute secondaries for users while keeping UM as primary for the new replica set
  const UMSpId = (await audiusLibs.ethContracts.ServiceProviderFactoryClient.getServiceProviderInfoFromEndpoint(USER_METADATA_ENDPOINT)).spID

  console.log('\nComputing replica sets....')

  let userIdToRSet = {}
  userIds.forEach(id => {
    // Randomly select two secondaries from spIds
    let replicaSet = [] // TODO: remove this primary
    let secondary1Index = Math.floor(Math.random(0) * spIds.length)
    let secondary2Index = -1
    while (secondary2Index === -1 || secondary1Index === secondary2Index) {
      secondary2Index = Math.floor(Math.random(0) * spIds.length)
    }

    replicaSet.push(spIds[secondary1Index])
    replicaSet.push(spIds[secondary2Index])

    userIdToRSet[id] = replicaSet

    // Keep track of number of times the secondary was chosen
    spIdToEndpointAndCount[spIds[secondary1Index]].selected += 1
    spIdToEndpointAndCount[spIds[secondary2Index]].selected += 1
  })

  // Print out user-to-rset mapping
  console.log('<userIds - replica sets>:\n', userIdToRSet)
  // Print out all healthy, non-Audius SPs to # of times they were assigned as secondaries
  console.log('<service providers - number of times selected as secondary>:\n', spIdToEndpointAndCount, '\n')

  // Write data to file
  writeDataToFile(spIdToEndpointAndCount, userIdToRSet)

  // Trigger sync for newly selected secondaries
  // TODO: consider sync size / batching the sync
  console.log(`\nSyncing across new secondaries....`)
  let userIdToRSetArr = Object.entries(userIdToRSet)
  for (i = 0; i < userIds.length; i++) {
    const userId = userIdToRSetArr[i][0]
    const replicaSetSPIds = userIdToRSetArr[i][1]

    console.log(`Processing userId=${userId} to from primary=${USER_METADATA_ENDPOINT} -> secondaries=${spIdToEndpointAndCount[replicaSetSPIds[0]].endpoint},${spIdToEndpointAndCount[replicaSetSPIds[1]].endpoint}`)

    // Sync UM data to newly selected secondaries
    await Promise.all(
      replicaSetSPIds
        .map(spId => {
          return syncSecondary({
            primary: USER_METADATA_ENDPOINT,
            secondary: spIdToEndpointAndCount[spId].endpoint,
            wallet: userIdToWallet[userId]
          })
        })
    )

    // TODO: make smarter maybe
    console.log(`Waiting ${SYNC_WAIT_TIME}ms for syncs to propogate`)
    await Util.wait(SYNC_WAIT_TIME)

    // Check that the clock values match the clock values on UM
    const clockValuesAcrossRSet = await Promise.all(
      [UMSpId, ...replicaSetSPIds]
        .map(spId =>
          getClockValue({
            endpoint: spId === 0 ? USER_METADATA_ENDPOINT : spIdToEndpointAndCount[spId].endpoint,
            wallet: userIdToWallet[userId],
            id: spId
          })
        )
    )

    const UMClockValue = clockValuesAcrossRSet[0].clockValue

    console.log(`userId=${userId} | UM clock value=${UMClockValue}`)
    clockValuesAcrossRSet.forEach(clockValueResp => {
      if (clockValueResp.endpoint !== USER_METADATA_ENDPOINT) {
        console.log(`userId=${userId} | secondary=${clockValueResp.endpoint} | clock value=${clockValueResp.clockValue}`)
        if (UMClockValue !== clockValueResp.clockValue) {
          const errorMsg = `Mismatch in clock values for userId=${userId}:\nUser Metadata primary clock value=${UMClockValue} | ${clockValueResp.endpoint} clock value=${clockValueResp.clockValue}`
          console.error(errorMsg)
          throw new Error(errorMsg)
        }
      }
    })

    console.log('Success!')

    // If clock values are all synced, write to new contract
    await setReplicaSet({
      audiusLibs,
      primarySpId: UMSpId,
      secondary1SpId: replicaSetSPIds[0],
      secondary2SpId: replicaSetSPIds[1],
      userId
    })
  }

  const end = Date.now() - start
  console.log(`\nTime Taken: ${end}ms`)
}

run()
