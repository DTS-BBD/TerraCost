# Test Terraform file for TerraCost extension testing

resource "aws_instance" "test_instance" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
  
  tags = {
    Name = "test-instance"
  }
}

resource "aws_s3_bucket" "test_bucket" {
  bucket = "test-terracost-bucket-12345"
  
  tags = {
    Name = "test-bucket"
  }
}

resource "aws_lambda_function" "test_function" {
  filename         = "test.zip"
  function_name    = "test-function"
  role            = "arn:aws:iam::123456789012:role/lambda-role"
  handler         = "index.handler"
  runtime         = "python3.9"
  
  tags = {
    Name = "test-lambda"
  }
}
