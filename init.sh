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
