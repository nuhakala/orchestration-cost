
# Curling

**NOTE when curling** we need to define the domain to the knative network
provider when deploying knative , and we need to give the domain in host header when
curling. **IMPORTANT THING TO NOTE IS THAT THE DOMAIN TO GIVE WHEN CURLING IS
SHOW WITH COMMAND `kubectl get ksvc -A` AND IT CONTAINS SOME KNATIVE PREFIX!**

# Network providers

Architecture of knative services:
https://knative.dev/docs/serving/architecture/#diagram

# How to make it work

Install kubeedge with edgemesh (gateway not needed). Then install knative with
kourier. Make sure to install knative before joining edge node, because the
knative containers won't start in edge node. After that deploying basic knative
service should be pingable from the cloud node given that the service is
properly exposed.

# RPI

Deploying knative to RPI does not work out of the box because kourier uses envoy
proxy, and envoy proxy has some BS problem with RPI page size of whatever:
https://github.com/envoyproxy/envoy/issues/23339

Solution is to either recompile RPI kernel or build your own envoy image with
custom arguments which disable tcmalloc.

I was reluctant to do either, desided do go with custom envoy image because I
don't want to run tests again after recompiling the kernel. Using image
thegrandpkizzle/envoy:1.26.1 which is built with tcmalloc disabled.
