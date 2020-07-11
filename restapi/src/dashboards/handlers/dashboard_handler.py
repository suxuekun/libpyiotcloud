

# from dashboards.services.dashboard_service import DashboardService, RemovingChartParam
# from dashboards.ioc import init_dashboard_service

# class DashboardHandler:
    
#     def __init__(self, dashboardService: DashboardService):
#         self.dashboardService = dashboardService
    
#     def removeChart(self, chartId):
#         result = self.dashboardService.remove_chart_gateway(chartId)
#         return result
    
#     def remove_many_chart_in_dashboards(self, chartsWithDashboard: {}):
#         result = self.dashboardService.remove_many_charts_in_many_dashboards(chartsWithDashboard)
#         return result


# dashboardHandler = DashboardHandler(init_dashboard_service())

# def get_dashoard_handler() -> DashboardHandler:
#     return dashboardHandler