FROM python:2.7.10

# Install requirements
ADD ./src/requirements.txt /var/tests/requirements.txt
RUN pip install -r /var/tests/requirements.txt --force-reinstall --upgrade -I

# Add tests
ADD ./src /var/tests/

# Run tests
WORKDIR /var/tests
CMD py.test --verbose tests.py
