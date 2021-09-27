#! /bin/bash
rm -r ./client
cd ../expert-coder-client
npm run build
cd ../expert-coder-server
mkdir client
cp -r ../expert-coder-client/dist/* ./client