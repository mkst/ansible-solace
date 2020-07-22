
# --------------------------------------------------------------------------
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
# --------------------------------------------------------------------------

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ansible-solace",
    version="0.4.0",
    author="Solace Corporation",
    author_email="ricardo.gomez-ulmke@solace.com",
    description="Ansible modules to configure Solace PubSub+ event brokers with SEMP(v2).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/solace-iot-team/ansible-solace",
    project_urls={
        "Source": "https://github.com/solace-iot-team/ansible-solace",
        "Tracker": "https://github.com/solace-iot-team/ansible-solace/issues",
    },
    license='MIT License',
    package_dir={'': 'lib'},
    packages=[
        'ansible/module_utils/network/solace',
        'ansible/modules/network/solace',
        'ansible/plugins/doc_fragments'
        ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Networking"
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests>=2.24.0'
    ],
    keywords='solace sempv2 ansible pubsub+'
)
