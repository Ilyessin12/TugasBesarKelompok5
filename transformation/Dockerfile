# Use Python with Spark base image
FROM apache/spark-py:latest

# Set working directory
WORKDIR /app

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    wget \
    openjdk-11-jdk \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download MongoDB Spark Connector JARs
RUN wget -P /app https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/3.0.1/mongo-spark-connector_2.12-3.0.1.jar \
    && wget -P /app https://repo1.maven.org/maven2/org/mongodb/mongo-java-driver/3.12.10/mongo-java-driver-3.12.10.jar

# Copy application code
COPY src/financialreport_transformer.py .
COPY src/news_transformer.py .
COPY src/main.py .

# Set environment variables for Spark
ENV SPARK_JARS=/app/mongo-spark-connector_2.12-3.0.1.jar,/app/mongo-java-driver-3.12.10.jar

# Command to run the application
CMD ["python3", "main.py"]