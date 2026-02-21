using HumiditySensorApp.Services;
using HumiditySensorApp.ViewModels;
using HumiditySensorApp.Views;
using LiveChartsCore.SkiaSharpView.Maui;
using SkiaSharp.Views.Maui.Controls.Hosting;

namespace HumiditySensorApp;

public static class MauiProgram
{
    public static MauiApp CreateMauiApp()
    {
        var builder = MauiApp.CreateBuilder();
        builder
            .UseMauiApp<App>()
            .UseSkiaSharp()
            .UseLiveCharts()
            .ConfigureFonts(fonts =>
            {
                fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
            });

        // HttpClient
        builder.Services.AddHttpClient<ISensorApiService, SensorApiService>(client =>
        {
            client.BaseAddress = new Uri("http://raspberrypizero:3000");
            client.Timeout = TimeSpan.FromSeconds(10);
        });

        // ViewModels
        builder.Services.AddTransient<DashboardViewModel>();
        builder.Services.AddTransient<ChartsViewModel>();
        builder.Services.AddTransient<ManagementViewModel>();

        // Pages
        builder.Services.AddTransient<DashboardPage>();
        builder.Services.AddTransient<ChartsPage>();
        builder.Services.AddTransient<ManagementPage>();

        return builder.Build();
    }
}
