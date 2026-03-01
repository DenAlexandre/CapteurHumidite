using HumiditySensorApp.Services;
using HumiditySensorApp.ViewModels;
using HumiditySensorApp.Views;
using LiveChartsCore.SkiaSharpView.Maui;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Options;
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

        builder.Services.AddHttpClient<ISensorApiService, SensorApiService>((sp, client) =>
        {
            var config = sp.GetRequiredService<IConfiguration>();
            client.BaseAddress = new Uri(config["SensorApi:BaseAddress"]!);
            client.Timeout = TimeSpan.FromSeconds(config.GetValue<int>("SensorApi:TimeoutSeconds"));
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
