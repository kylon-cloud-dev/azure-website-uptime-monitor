output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "storage_account_name" {
  value = azurerm_storage_account.main.name
}

output "storage_table_name" {
  value = azurerm_storage_table.uptime_checks.name
}

output "function_app_name" {
  value = azurerm_linux_function_app.monitor.name
}

output "application_insights_name" {
  value = azurerm_application_insights.main.name
}

output "log_analytics_workspace_name" {
  value = azurerm_log_analytics_workspace.main.name
}