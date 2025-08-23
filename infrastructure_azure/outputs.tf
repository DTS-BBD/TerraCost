output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "vm_name" {
  value = azurerm_virtual_machine.main.name
}

output "sql_server_name" {
  value = var.sql_enabled ? azurerm_sql_server.main[0].name : null
}
