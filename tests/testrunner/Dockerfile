FROM python:2.7.10

# Add tests
ADD ./src /var/tests/

# Install requirements
ADD ./src/requirements.txt /var/tests/requirements.txt
RUN pip install -r /var/tests/requirements.txt --force-reinstall --upgrade -I


# Run tests
WORKDIR /var/tests
CMD py.test --verbose tests.py
