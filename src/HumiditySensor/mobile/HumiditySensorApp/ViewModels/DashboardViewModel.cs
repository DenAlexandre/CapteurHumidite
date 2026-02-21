using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using HumiditySensorApp.Services;

namespace HumiditySensorApp.ViewModels;

public partial class DashboardViewModel : ObservableObject
{
    private readonly ISensorApiService _api;
    private IDispatcherTimer? _timer;

    [ObservableProperty]
    private double _temperature;

    [ObservableProperty]
    private double _humidity;

    [ObservableProperty]
    private int _setpoint;

    [ObservableProperty]
    private bool _isVentilationOn;

    [ObservableProperty]
    private bool _isHumidityOverSetpoint;

    [ObservableProperty]
    private bool _isLoading;

    [ObservableProperty]
    private bool _isRefreshing;

    [ObservableProperty]
    private bool _hasError;

    [ObservableProperty]
    private string _errorMessage = string.Empty;

    [ObservableProperty]
    private bool _isWaiting;

    [ObservableProperty]
    private string _waitingMessage = string.Empty;

    private bool _hasLoadedOnce;

    public DashboardViewModel(ISensorApiService api)
    {
        _api = api;
    }

    public void StartAutoRefresh(IDispatcher dispatcher)
    {
        _timer = dispatcher.CreateTimer();
        _timer.Interval = TimeSpan.FromSeconds(30);
        _timer.Tick += async (s, e) => await LoadDataAsync();
        _timer.Start();
    }

    public void StopAutoRefresh()
    {
        _timer?.Stop();
    }

    [RelayCommand]
    private async Task LoadDataAsync()
    {
        if (Connectivity.Current.NetworkAccess != NetworkAccess.Internet)
        {
            IsWaiting = !_hasLoadedOnce;
            WaitingMessage = "Pas de connexion réseau.\nNouvelle tentative dans 30s...";
            HasError = _hasLoadedOnce;
            ErrorMessage = "Pas de connexion réseau";
            IsRefreshing = false;
            return;
        }

        if (!_hasLoadedOnce && !IsRefreshing)
            IsWaiting = true;

        WaitingMessage = "Connexion au capteur...";
        IsLoading = !IsRefreshing && _hasLoadedOnce;
        HasError = false;

        try
        {
            var humidityTask = _api.GetHumidityAsync();
            var configTask = _api.GetConfigAsync();
            await Task.WhenAll(humidityTask, configTask);

            var reading = humidityTask.Result;
            var config = configTask.Result;

            Temperature = Math.Round(reading.Temperature, 1);
            Humidity = Math.Round(reading.Humidity, 1);
            Setpoint = config.Setpoint;
            IsVentilationOn = config.IsManualMode;
            IsHumidityOverSetpoint = reading.Humidity > config.Setpoint;
            _hasLoadedOnce = true;
            IsWaiting = false;
        }
        catch (Exception ex)
        {
            if (!_hasLoadedOnce)
            {
                IsWaiting = true;
                WaitingMessage = "Serveur indisponible.\nNouvelle tentative dans 30s...";
            }
            else
            {
                HasError = true;
                ErrorMessage = $"Erreur : {ex.Message}";
            }
        }
        finally
        {
            IsLoading = false;
            IsRefreshing = false;
        }
    }

    [RelayCommand]
    private async Task RefreshAsync()
    {
        IsRefreshing = true;
        await LoadDataAsync();
    }
}
