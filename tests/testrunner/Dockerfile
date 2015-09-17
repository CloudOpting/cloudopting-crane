FROM python:2.7.10

# Install requirements
ADD ./requirements.txt /var/tests/requirements.txt
RUN pip install -r /var/tests/requirements.txt --force-reinstall --upgrade -I

# Add tests
ADD ./tests.py /var/tests/tests.py

# Run tests
WORKDIR /var/tests
CMD python tests.py
