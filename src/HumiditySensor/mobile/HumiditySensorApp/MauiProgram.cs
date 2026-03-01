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


        var config = new ConfigurationBuilder()
            .AddJsonStream(
                FileSystem.OpenAppPackageFileAsync("appsettings.json")
                          .GetAwaiter()
                          .GetResult())
            .Build();

        builder.Configuration.AddConfiguration(config);

        // API Settings (persistant via Preferences, fallback sur appsettings.json)
        var defaultUrl = builder.Configuration["SensorApi:BaseAddress"] ?? "http://raspberrypizero:3000";
        builder.Services.AddSingleton<IApiSettingsService>(new ApiSettingsService(defaultUrl));

        var timeoutSeconds = builder.Configuration.GetValue<int?>("SensorApi:TimeoutSeconds") ?? 10;
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
