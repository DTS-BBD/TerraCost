variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "terracost-demo"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "vm_size" {
  description = "Size of the virtual machine"
  type        = string
  default     = "Standard_D4s_v3"
}

variable "sql_enabled" {
  description = "Enable SQL Database"
  type        = bool
  default     = true
}

variable "sql_admin_username" {
  description = "SQL Server admin username"
  type        = string
  default     = "sqladmin"
}

variable "sql_admin_password" {
  description = "SQL Server admin password"
  type        = string
  default     = "P@ssw0rd123!"
}

variable "sql_tier" {
  description = "SQL Database service tier"
  type        = string
  default     = "Premium"
}
