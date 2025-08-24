# Multi-Cloud Infrastructure Test
# This file demonstrates TerraCost's ability to estimate costs across AWS, Azure, and GCP

# =============================================================================
# AWS Resources
# =============================================================================

resource "aws_instance" "test_ec2" {
  ami           = "ami-12345678"
  instance_type = "t3.micro"
  
  tags = {
    Name = "test-ec2-instance"
  }
}

resource "aws_s3_bucket" "test_bucket" {
  bucket = "test-terracost-bucket"
  
  tags = {
    Name = "test-s3-bucket"
  }
}

# =============================================================================
# Azure Resources
# =============================================================================

resource "azurerm_resource_group" "test_rg" {
  name     = "test-resource-group"
  location = "eastus"
}

resource "azurerm_virtual_machine" "test_vm" {
  name                  = "test-vm"
  location              = azurerm_resource_group.test_rg.location
  resource_group_name   = azurerm_resource_group.test_rg.name
  network_interface_ids = [azurerm_network_interface.test_nic.id]
  vm_size               = "Standard_B1s"

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  storage_os_disk {
    name              = "test-os-disk"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Standard_LRS"
  }

  os_profile {
    computer_name  = "test-vm"
    admin_username = "testadmin"
  }

  os_profile_linux_config {
    disable_password_authentication = true
    ssh_keys {
      path     = "/home/testadmin/.ssh/authorized_keys"
      key_data = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
    }
  }
}

resource "azurerm_network_interface" "test_nic" {
  name                = "test-nic"
  location            = azurerm_resource_group.test_rg.location
  resource_group_name = azurerm_resource_group.test_rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.test_subnet.id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_virtual_network" "test_vnet" {
  name                = "test-vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.test_rg.location
  resource_group_name = azurerm_resource_group.test_rg.name
}

resource "azurerm_subnet" "test_subnet" {
  name                 = "test-subnet"
  resource_group_name  = azurerm_resource_group.test_rg.name
  virtual_network_name = azurerm_virtual_network.test_vnet.name
  address_prefixes     = ["10.0.1.0/24"]
}

resource "azurerm_storage_account" "test_storage" {
  name                     = "teststorageaccount123"
  resource_group_name      = azurerm_resource_group.test_rg.name
  location                 = azurerm_resource_group.test_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# =============================================================================
# GCP Resources
# =============================================================================

resource "google_project" "test_project" {
  name       = "Test TerraCost Project"
  project_id = "test-terracost-project-123"
}

resource "google_compute_instance" "test_gcp_vm" {
  name         = "test-gcp-vm"
  machine_type = "f1-micro"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    network = "default"
    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    ssh-keys = "testuser:ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."
  }
}

resource "google_storage_bucket" "test_gcp_bucket" {
  name          = "test-terracost-gcp-bucket"
  location      = "US"
  force_destroy = true

  uniform_bucket_level_access = true
}

resource "google_cloud_sql_instance" "test_sql" {
  name             = "test-sql-instance"
  database_version = "MYSQL_5_7"
  region           = "us-central1"

  settings {
    tier = "db-f1-micro"
  }

  deletion_protection = false
}

resource "google_container_cluster" "test_gke" {
  name     = "test-gke-cluster"
  location = "us-central1"

  remove_default_node_pool = true
  initial_node_count       = 1

  master_auth {
    username = ""
    password = ""

    client_certificate_config {
      issue_client_certificate = false
    }
  }
}

resource "google_container_node_pool" "test_node_pool" {
  name       = "test-node-pool"
  location   = "us-central1"
  cluster    = google_container_cluster.test_gke.name
  node_count = 1

  node_config {
    machine_type = "e2-micro"

    oauth_scopes = [
      "https://www.googleapis.com/auth/logging.write",
      "https://www.googleapis.com/auth/monitoring",
    ]

    metadata = {
      disable-legacy-endpoints = "true"
    }

    labels = {
      app = "test"
    }

    tags = ["test"]
  }
}
