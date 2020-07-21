# TEST-Tests

Work in progress. Does not fit with Ansible testing strategy nor CI/CD.

Module tests and test runner.

## Run all Tests
Multiple brokers:
- 1 cloud instance
- pulls down multiple versions of pubsub+ standard docker images

````bash
# run all tests
./run.sh
````

## Run Single Test

````bash
# start & stop a local broker
./start.local.broker.sh
./stop.local.broker.sh
````

````bash
cd <test-directory>

./run.sh
````
---
The End.
