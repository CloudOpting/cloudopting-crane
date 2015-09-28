FROM python:2.7.10

# Add tests
ADD ./src /var/tests/

# Install requirements
ADD ./src/requirements.txt /var/tests/requirements.txt
WORKDIR /var/tests
RUN pip install -r ./requirements.txt --force-reinstall --upgrade -I
# Run tests
CMD py.test --verbose tests.py
