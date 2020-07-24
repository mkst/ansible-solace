#!/bin/bash
# ---------------------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2020, Solace Corporation, Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ---------------------------------------------------------------------------------------------

#SCRIPT_NAME=$(basename $(test -L "$0" && readlink "$0" || echo "$0"));
SCRIPT_PATH=$(cd $(dirname "$0") && pwd);
# test jq is installed
res=$(jq --version)
if [[ $? != 0 ]]; then echo "ERR >>> jq not found. aborting."; echo; exit 1; fi
source $SCRIPT_PATH/lib/functions.sh


clear
echo; echo "##############################################################################################################"
echo


##############################################################################################################################
# Prepare

#export ANSIBLE_SOLACE_TEST_RUNNER_ENV="dev"
#export ANSIBLE_SOLACE_TEST_RUNNER_ENV="package"

env=$(chooseTestRunnerEnv $ANSIBLE_SOLACE_TEST_RUNNER_ENV)
if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
echo; echo "Running tests with environment: $env ..."; echo
export ANSIBLE_SOLACE_TEST_RUNNER_ENV=$env

source $SCRIPT_PATH/lib/unset-all.sh
if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi

export ANSIBLE_SOLACE_ENABLE_LOGGING=false
export ANSIBLE_PYTHON_INTERPRETER=/usr/local/bin/python

if [[ $ANSIBLE_SOLACE_TEST_RUNNER_ENV == "dev" ]]; then
  export ANSIBLE_SOLACE_HOME="$SCRIPT_PATH/.."
  export ANSIBLE_MODULE_UTILS="$ANSIBLE_SOLACE_HOME/lib/ansible/module_utils"
  export ANSIBLE_LIBRARY="$ANSIBLE_SOLACE_HOME/lib/ansible/modules"
fi

##############################################################################################################################
# set test scripts

ansibleSolaceTests=(
  "wait_until_brokers_available" # this must go first in the list
  "solace_mqtt_session"
  "solace_rdp"
  "solace_get_facts"
  "solace_queue"
  "solace_get_queues"
  "solace_get_client_usernames"
  "solace_acl_profile"
)

##############################################################################################################################
# set Files

localBrokerInventoryFile="$SCRIPT_PATH/lib/local.broker.inventory.json"
cloudBrokersInventoryFile="$SCRIPT_PATH/lib/cloud.brokers.inventory.json"
dockerComposeYmlFile="$SCRIPT_PATH/lib/PubSubStandard_singleNode.yml"

if [ ! -f "$localBrokerInventoryFile" ]; then echo "ERR >>> aborting. $localBrokerInventoryFile does not exist."; exit 1; fi
if [ ! -f "$cloudBrokersInventoryFile" ]; then echo "ERR >>> aborting. $cloudBrokersInventoryFile does not exist."; exit 1; fi
if [ ! -f "$dockerComposeYmlFile" ]; then echo "ERR >>> aborting. $dockerComposeYmlFile does not exist."; exit 1; fi


##############################################################################################################################
# set broker images

brokerDockerImageLatest="solace/solace-pubsub-standard:latest"

brokerDockerImagesFile="$SCRIPT_PATH/lib/brokerDockerImages.json"
brokerDockerImagesJSON=$(cat $brokerDockerImagesFile | jq -r '.brokerDockerImages' )
brokerDockerImagesArray=($(echo $brokerDockerImagesJSON | jq -r '.[]'))

echo; echo "Broker docker images:"; echo
for i in "${!brokerDockerImagesArray[@]}"; do
  echo " $i: '${brokerDockerImagesArray[$i]}'" 1>&2
done

brokerDockerContainerName="pubSubStandardSingleNode"
echo; echo "Broker docker container:"; echo;
echo " name: '$brokerDockerContainerName'"
echo

##############################################################################################################################
# loop 1:
# - remove all containers, remove latest image, pull all images,

echo; echo "Removing all docker containers ..."
docker rm -f "$brokerDockerContainerName"
# if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
echo "Done."

echo; echo "Removing latest docker image: $brokerDockerImageLatest ..."
docker rmi -f "$brokerDockerImageLatest"
# if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
echo "Done."

echo; echo "Pulling all docker images from docker hub..."; echo
for i in "${!brokerDockerImagesArray[@]}"; do
  brokerDockerImage=${brokerDockerImagesArray[$i]}
  echo; docker pull $brokerDockerImage
  if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
done
echo; echo "Done."
echo; echo "List of docker images:"; echo
docker images | grep solace/
echo; echo "Done."


##############################################################################################################################
# run tests against cloud brokers

for ansibleSolaceTest in ${ansibleSolaceTests[@]}; do

  runScript="$SCRIPT_PATH/$ansibleSolaceTest/_run.call.sh $cloudBrokersInventoryFile"

  echo; echo "##############################################################################################################"
  echo "# Cloud broker test: $ansibleSolaceTest"
  echo "# calling: $runScript"

  $runScript

  if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi

done

##############################################################################################################################
# loop 2:
# - start container, run tests against local brokers

for i in "${!brokerDockerImagesArray[@]}"; do

  brokerDockerImage=${brokerDockerImagesArray[$i]}

  echo; echo "Starting container with image: $brokerDockerImage ..."

  docker rm -f $brokerDockerContainerName
  #if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi

  export brokerDockerImage
  export brokerDockerContainerName
  docker-compose -f $dockerComposeYmlFile up -d
  if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi

  for ansibleSolaceTest in ${ansibleSolaceTests[@]}; do

    runScript="$SCRIPT_PATH/$ansibleSolaceTest/_run.call.sh $localBrokerInventoryFile"

    echo; echo "##############################################################################################################"
    echo "# Local broker test: $ansibleSolaceTest"
    echo "# image: $brokerDockerImage"
    echo "# calling: $runScript"

    $runScript

    if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi

  done

done

echo;
echo "##############################################################################################################"
echo "# All tests completed successfully!"
echo;
##############################################################################################################################
# loop 3:
# - remove all containers, remove all images

echo; echo "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"; echo
echo "! WARNING: NOT REMOVING CONTAINERS NOR IMAGES !"
echo; exit 1; echo

echo; echo "Removing all docker containers ..."
docker rm -f "$brokerDockerContainerName"
if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
echo "Done."

echo; echo "Removing all docker images ..."
for brokerDockerImage in ${brokerDockerImages[@]}; do
  docker rmi -f $brokerDockerImage
  if [[ $? != 0 ]]; then echo "ERR >>> aborting."; echo; exit 1; fi
done



###
# The End.
