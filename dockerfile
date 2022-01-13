FROM python:3.10.0b2

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory to /automation-framework-mock-api
WORKDIR /app

# Install any needed packages
RUN apt-get update \
&&  rm -rf /var/lib/apt/lists/* \
&& pip install .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Unit tests
RUN pytest --cov owasp_zap_historic --cov-report term-missing --cov-config=test/.coveragerc -v test/function_test.py

# Run the owasp-zap-historic flask with argument to connect to db
# Below command is to run in docker container pointed to local mysql
# CMD owaspzaphistoric -s '192.168.86.248'
# Then in CMD window docker run -p 5000:5000 owaspzaphistoric
# Below command is to run on Rancher and connect to mysql db shared with RFH
CMD owaspzaphistoric -s "${SQLHOST}" -t "${PORT}" -u "${USERNAME}" -p "${PASSWORD}" -a "${FLASKHOST}"
