# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from pyecharts.charts import Bar
from pyecharts import options as opts

def hello(request):
    return HttpResponse("Hello World")

def oil_history_price(request):
    return render(request, 'oil_history_price_rander.html')

class LineChartJSONView(BaseLineChartView):
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_providers(self):
        """Return names of datasets."""
        return ["Central", "Eastside", "Westside"]

    def get_data(self):
        """Return 3 datasets to plot."""

        return [[75, 44, 92, 11, 44, 95, 35],
                [41, 92, 18, 3, 73, 87, 92],
                [87, 21, 94, 3, 90, 13, 65]]

def pychartsexample(request):#打印出圖片頁面
    bar = Bar()
    bar.add_xaxis(["衬衫", "毛衣", "领带", "裤子", "风衣", "高跟鞋", "袜子"])
    bar.add_yaxis("商家A", [114, 55, 27, 101, 125, 27, 105])
    bar.add_yaxis("商家B", [57, 134, 137, 129, 145, 60, 49])
    bar.set_global_opts(title_opts=opts.TitleOpts(title="某商场销售情况"))
    a = bar.render()
    print(a.split('\\')[-1])
    return render(request, a.split('\\')[-1])

line_chart = TemplateView.as_view(template_name='django_chartjs_example.html')
line_chart_json = LineChartJSONView.as_view()