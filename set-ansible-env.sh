#!/bin/bash
# --------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2020 Ricardo Gomez-Ulmke (ricardo.gomez-ulmke@solace.com)
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
# --------------------------------------------------------------------------

################################################################################
# usage: source set-ansible-env.sh
#
# Prepend ansible-solace path to ansible env vars

######
#
# Set the location of ansible-solace installation.
# pip3 show ansible-solace
# copy the Location: <ansible-solace-install-location>
# paste to ANSIBLE_SOLACE_HOME
#
######


export ANSIBLE_SOLACE_HOME="ansible-solace-location"

###
# dont' change
if [[ -z $ANSIBLE_MODULE_UTILS ]]; then COLON=""; else COLON=":"; fi
export ANSIBLE_MODULE_UTILS="$ANSIBLE_SOLACE_HOME/ansible/module_utils$COLON$ANSIBLE_MODULE_UTILS"
if [[ -z $ANSIBLE_LIBRARY ]]; then COLON=""; else COLON=":"; fi
export ANSIBLE_LIBRARY="$ANSIBLE_SOLACE_HOME/ansible/modules$COLON$ANSIBLE_LIBRARY"

clear
echo
echo "Prepending ansible-solace path to ansible env vars:"; echo
echo "ANSIBLE_SOLACE_HOME=$ANSIBLE_SOLACE_HOME"
echo "ANSIBLE_MODULE_UTILS=$ANSIBLE_MODULE_UTILS"
echo "ANSIBLE_LIBRARY=$ANSIBLE_LIBRARY"
echo

###
# The End.
