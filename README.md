# Web_GCP-Manga-Translator

## Application

- Create project on GCP
- Enable required APIs (can be done as we go along)
- Create cloud storage buckets in the console
- Create functions in the cloud functions section in the console. Use the code in the 'functions' directory in the github repository for all three functions.
    
    ocr-extract => Trigger is 'sde-mangas' bucket. Start point will be 'process_img'
    ocr-translate => Trigger is 'translation-reqs' topic. Start point will be 'translate'
    ocr-save =>  Trigger is 'translation-results' topic. Start point will be 'save'

- Open project in cloud shell in the console. Enter the following commands in the shell

```
git clone https://github.com/saurabhburewar/Web_GCP-Manga-Translator
```
```
cd Web_GCP-Manga-Translator
```
```
cd app
```
```
pip3 install -r requirements.txt --user
```
```
pip3 install gunicorn --user
```

- The following will run the application in the cloud shell. Use web preview on port 8080 to view the webpage.
```
~/.local/bin/gunicorn -b :8080 main:app
```

- Next, we create an instance 
```
gcloud compute instances create sde-instance1 \
    --image-family=debian-10 \
    --image-project=debian-cloud \
    --machine-type=g1-small \
    --scopes userinfo-email,cloud-platform \
    --metadata-from-file startup-script=startup.sh \
    --zone us-central1-a \
    --tags http-server
```
- To check the status of the instance
```
gcloud compute instances get-serial-port-output sde-instance1 --zone us-central1-a
```
- Create Firewall rules 
```
gcloud compute firewall-rules create default-allow-http-8080 \
    --allow tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --target-tags http-server \
    --description "Allow port 8080 access to http-server"
```
- Application is hosted on the external IP address of the VM instance. 

## Load balancing 

- Create the instance template like your instances
- Create an instance group using the template and add a named port to the instance group
- Reserve external IP addresses for our load balancer
- Configure a load balancer

    On load balancing page, HTTP load balancing,
    Backend configuration using instance group we made earlier.
    Also, create a http health check
    Frontend configuration, configure a forwarding rule
    Create the load balancer

- Connect to the load balancer and send traffic to instances according to location

## Demo video
Demo - https://youtu.be/7xOWBCW6QCk

## Report
Read full report [here](https://github.com/saurabhburewar/Web_GCP-Manga-Translator/blob/main/Report.pdf).
