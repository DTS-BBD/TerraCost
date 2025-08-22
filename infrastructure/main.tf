provider "aws" {
  region = var.aws_region
}

module "iam" {
  source       = "./modules/iam"
  project_name = var.project_name
}

module "vpc" {
  source       = "./modules/vpc"
  project_name = var.project_name
  vpc_cidr     = var.vpc_cidr
  aws_region   = var.aws_region
  public_subnet_count = 2
  trusted_ssh_ips = var.trusted_ssh_ips
}

module "internet_gateway" {
  source           = "./modules/internet_gateway"
  project_name     = var.project_name
  vpc_id           = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
}

module "ec2" {
  source         = "./modules/ec2"
  project_name   = var.project_name
  subnet_ids     = module.vpc.public_subnet_ids
  instance_count = var.ec2_instance_count
  aws_region     = var.aws_region
  security_group_id = module.vpc.default_security_group_id
  iam_instance_profile = module.iam.iam_instance_profile_name
  key_name = var.key_name
}

module "rds" {
  source                 = "./modules/rds"
  project_name           = var.project_name
  subnet_ids             = module.vpc.public_subnet_ids
  vpc_security_group_ids = [module.vpc.default_security_group_id]
  aws_region             = var.aws_region
  enabled                = var.rds_enabled
  db_password            = var.db_password
  db_username            = var.db_username
  db_name                = var.db_name
  publicly_accessible    = false
}

module "budget" {
  source       = "./modules/budget"
  project_name = var.project_name
  budget_emails = var.budget_emails
}