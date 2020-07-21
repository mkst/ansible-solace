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

SCRIPT=`realpath -s $0`
SCRIPT_PATH=`dirname $SCRIPT`

BROKERS_ARG=$1

##############################################################################################################################
# Prepare

ANSIBLE_SOLACE_LOG_FILE="$SCRIPT_PATH/ansible-solace.log"
rm -f $ANSIBLE_SOLACE_LOG_FILE

##############################################################################################################################
# Run

BROKERS_INVENTORY="$SCRIPT_PATH/../lib/brokers.inventory.json"
PLAYBOOK="$SCRIPT_PATH/wait_until_brokers_available.playbook.yml"
BROKERS="all"
if [ ! -z "$BROKERS_ARG" ]; then BROKERS=$BROKERS_ARG; fi


# --step --check -vvv
ansible-playbook -i $BROKERS_INVENTORY \
                  $PLAYBOOK \
                  --extra-vars "brokers=$BROKERS" \
                  # -vvv

###
# The End.
