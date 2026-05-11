FROM varnish:7.4-alpine

# Copy VCL configuration
COPY default.vcl /etc/varnish/default.vcl

# Set default parameters
ENV VARNISH_SIZE=256m

# Expose port
EXPOSE 80

# Start Varnish
CMD ["varnishd", "-F", "-a", ":80", "-f", "/etc/varnish/default.vcl", "-s", "malloc,256m"]
