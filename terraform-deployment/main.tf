provider "aws" {
  region = "eu-north-1" # Stockholm region
}

# Define a security group to allow SSH access
resource "aws_security_group" "allow_ssh" {
  name        = "allow_ssh"
  description = "Allow SSH traffic"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Create an EC2 instance to run the scraper
resource "aws_instance" "scraper_instance" {
  ami           = "ami-02db68a01488594c5" # Amazon Linux 2023 AMI
  instance_type = "t2.micro"
  key_name      = aws_key_pair.scraper_key_pair.key_name
  security_groups = [aws_security_group.allow_ssh.name]

  tags = {
    Name = "scraper-instance"
  }

  # Install Docker on the EC2 instance and run the scraper
  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo amazon-linux-extras install docker
              sudo service docker start
              sudo usermod -a -G docker ec2-user
              sudo docker run -d ${var.docker_image_name} -e "BASE_API_URL=${var.base_api_url}" \
                                                          -e "CLIENT_ID=${var.client_id}" \
                                                          -e "CLIENT_SECRET=${var.client_secret}"
              EOF
}

# Define the key pair to SSH into the instance
resource "aws_key_pair" "scraper_key_pair" {
  key_name   = "scraper-key"
  public_key = file("~/.ssh/id_rsa.pub")
}

output "instance_ip" {
  description = "Public IP of the EC2 instance"
  value       = aws_instance.scraper_instance.public_ip
}
