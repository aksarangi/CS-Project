# backend/api/reports.py

from backend.reports.sales_summary import SalesSummaryReport
from backend.reports.stock_report import StockReport
from backend.utils.logger import logger

class ReportsAPI:
    """
    Central API to expose all reports for the frontend.
    Wraps SalesSummaryReport and StockReport.
    """

    def __init__(self):
        self.sales_report = SalesSummaryReport()
        self.stock_report = StockReport()

    # ----- Sales Summary -----
    def get_daily_sales(self):
        """
        Returns daily sales data.
        """
        return self.sales_report.get_daily_sales()

    def get_daily_sales_plot_data(self):
        """
        Returns data suitable for plotting daily sales.
        """
        return self.sales_report.get_daily_sales_plot_data()

    def get_top_selling_books(self, limit=10):
        """
        Returns top-selling books.
        """
        return self.sales_report.top_selling_books(limit=limit)

    # ----- Stock / Inventory -----
    def get_current_stock(self):
        """
        Returns current stock data for all books.
        """
        return self.stock_report.get_current_stock()

    def get_low_stock(self, threshold=10):
        """
        Returns books with stock below threshold.
        """
        return self.stock_report.get_low_stock(threshold=threshold)

    def get_category_stock_summary(self):
        """
        Returns category-wise stock summary.
        """
        return self.stock_report.get_category_stock_summary()
