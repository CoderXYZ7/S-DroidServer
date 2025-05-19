#!/bin/bash

API="http://tmhome.tplinkdns.com:3357"

echo "Testing /api/status"
curl -s "$API/api/status"; echo

echo "Testing /UpdateRepoList"
curl -s -X POST "$API/UpdateRepoList"; echo

echo "Testing /UpdateRepos"
curl -s -X POST "$API/UpdateRepos"; echo

echo "Testing /GetRepos"
curl -s "$API/GetRepos"; echo

echo "Testing /GetDetails/testrepo"
curl -s "$API/GetDetails/testrepo"; echo

echo "Testing /GetFile/testrepo/app.apk"
curl -s -O "$API/GetFile/testrepo/app.apk"

echo "Testing /GetFavicon/testrepo"
curl -s -O "$API/GetFavicon/testrepo"
