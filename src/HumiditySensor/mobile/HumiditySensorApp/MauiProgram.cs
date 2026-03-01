using HumiditySensorApp.Services;
using HumiditySensorApp.ViewModels;
using HumiditySensorApp.Views;
using LiveChartsCore.SkiaSharpView.Maui;
using Microsoft.Extensions.Configuration;
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

        // Configuration
        using var stream = FileSystem.OpenAppPackageFileAsync("appsettings.json").Result;
        var config = new ConfigurationBuilder()
            .AddJsonStream(stream)
            .Build();
        builder.Configuration.AddConfiguration(config);

        var apiBaseUrl = builder.Configuration["ApiSettings:BaseUrl"] ?? "http://raspberrypizero:3000";
        var timeoutSeconds = int.TryParse(builder.Configuration["ApiSettings:TimeoutSeconds"], out var t) ? t : 10;

        // API Settings
        builder.Services.AddSingleton<IApiSettingsService>(new ApiSettingsService(apiBaseUrl));

        // HttpClient
        builder.Services.AddHttpClient<ISensorApiService, SensorApiService>(client =>
        {
            client.Timeout = TimeSpan.FromSeconds(timeoutSeconds);
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
