# mad-dog
🐶 Creator Node Test Suite

## Usage
### Standing Up/Down Services:
1. If necessary, run `npm i` in `/mad-dog` and `/service-commands`
2. cd to `/libs` and run `npm link`
3. cd to `/service-commands` and run `npm link @audius/libs`
4. Run `npm link`
5. cd to `/mad-dog` and run `npm link @audius/service-commands`
6. If systems are already up, run `npm run start down`
7. Run `npm run start up`

**Note:** If tests fail, sometimes running `npm i` in `/libs` and relinking packages will help. Or, bring up a fresh set of local services.

### Running Tests
**Run all the tests in test suite**: 
- `npm run start <test name>`

**Run all the tests in test suite with specified account offset**: 
- `npm run start <test name> <0-99 offset of wallets in config.json>`

**Run all the tests in test suite in verbose mode (prints out container logs if tests fail)**: 
- `npm run start <test name> verbose` 
- `npm run start <test name> <0-99 offset of wallets in config.json> verbose` 

## Notes
- `service-commands` need to be linked, or the latest version published to npm.

## Code Structure
- The single test in mad-dog is based on the class `EmitterBasedTest`. This class
sets up a test that uses emitters to fire off events representing requests to our services, and then fires events for handling those responess. The test implementer is responsible for fleshing out listeners for emitted events. **To see an example of this, look at `tests/test_integration.js`**

- If you want to run tests without the emitter system, look at `tests/test_ipldBlacklist.js`

- `executeOne`? `executeAll`? These are just two helper functions that make it easier to perform libs operations in a test. `executeAll` performs some operation on every initted instance of libs in parallel, while `executeOne` takes in index and performs the operation against that instance of libs. Both functions accept a function that is passed an instance of libs:
```
const trackId = await executeOne(walletIndex, libs =>
  uploadTrack(libs, track, TRACK_DIR)
)
```
