# Use base
FROM cloudopting/ubuntubase:14.04
# Add puppet modules:
ADD modules /tmp/modules
# Add manifest to apply
ADD images/webconsumer/manifest.pp /tmp/manifest.pp
# Apply manifest
RUN puppet apply --modulepath=/tmp/modules /tmp/manifest.pp
