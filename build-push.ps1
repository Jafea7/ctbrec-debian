param (
  [Parameter(Mandatory = $true)][string]$version,
  [switch]$push = $false,
  [switch]$manifest = $false
)

docker build -f .\Dockerfile.amd64 . -t jafea7/ctbrec-debian:amd64_$version
docker build -f .\Dockerfile.aarch64 . -t jafea7/ctbrec-debian:arm64_$version
docker build -f .\Dockerfile.arm7l . -t jafea7/ctbrec-debian:arm7l_$version

if ($push) {
  docker push jafea7/ctbrec-debian:amd64_$version
  docker push jafea7/ctbrec-debian:arm64_$version
  docker push jafea7/ctbrec-debian:arm7l_$version
}
if ($manifest) {
  docker manifest rm jafea7/ctbrec-debian:latest
  docker manifest create jafea7/ctbrec-debian:latest jafea7/ctbrec-debian:arm7l_$version jafea7/ctbrec-debian:arm64_$version jafea7/ctbrec-debian:amd64_$version
  docker manifest inspect jafea7/ctbrec-debian:latest
  docker manifest push --purge jafea7/ctbrec-debian:latest
  
  docker manifest rm jafea7/ctbrec-debian:$version
  docker manifest create jafea7/ctbrec-debian:$version jafea7/ctbrec-debian:arm7l_$version jafea7/ctbrec-debian:arm64_$version jafea7/ctbrec-debian:amd64_$version
  docker manifest inspect jafea7/ctbrec-debian:$version
  docker manifest push --purge jafea7/ctbrec-debian:$version
}
