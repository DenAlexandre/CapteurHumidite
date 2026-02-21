using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using HumiditySensorApp.Services;

namespace HumiditySensorApp.ViewModels;

public partial class ManagementViewModel : ObservableObject
{
    private readonly ISensorApiService _api;

    [ObservableProperty]
    private int _setpoint = 50;

    [ObservableProperty]
    private bool _isManualMode;

    [ObservableProperty]
    private bool _isVentilationOn;

    [ObservableProperty]
    private bool _isLoading;

    [ObservableProperty]
    private bool _hasError;

    [ObservableProperty]
    private string _errorMessage = string.Empty;

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(SaveSetpointCommand))]
    [NotifyCanExecuteChangedFor(nameof(RebootCommand))]
    private bool _isWaiting;

    [ObservableProperty]
    private string _waitingMessage = string.Empty;

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(SaveSetpointCommand))]
    [NotifyCanExecuteChangedFor(nameof(RebootCommand))]
    private bool _isServerAvailable;

    private bool _hasLoadedOnce;

    public ManagementViewModel(ISensorApiService api)
    {
        _api = api;
    }

    private bool CanExecuteAction() => IsServerAvailable && !IsWaiting;

    [RelayCommand]
    private async Task LoadConfigAsync()
    {
        if (Connectivity.Current.NetworkAccess != NetworkAccess.Internet)
        {
            IsServerAvailable = false;
            IsWaiting = !_hasLoadedOnce;
            WaitingMessage = "Pas de connexion réseau";
            HasError = _hasLoadedOnce;
            ErrorMessage = "Pas de connexion réseau";
            return;
        }

        if (!_hasLoadedOnce)
            IsWaiting = true;

        WaitingMessage = "Connexion au capteur...";
        IsLoading = _hasLoadedOnce;
        HasError = false;

        try
        {
            var config = await _api.GetConfigAsync();
            Setpoint = config.Setpoint;
            IsManualMode = config.IsManualMode;
            _hasLoadedOnce = true;
            IsServerAvailable = true;
            IsWaiting = false;
        }
        catch (Exception ex)
        {
            IsServerAvailable = false;
            if (!_hasLoadedOnce)
            {
                IsWaiting = true;
                WaitingMessage = "Serveur indisponible.\nAppuyez pour réessayer.";
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
        }
    }

    [RelayCommand(CanExecute = nameof(CanExecuteAction))]
    private async Task SaveSetpointAsync()
    {
        HasError = false;
        try
        {
            await _api.SetConfigAsync("cons_hum", Setpoint.ToString());
        }
        catch (Exception ex)
        {
            IsServerAvailable = false;
            HasError = true;
            ErrorMessage = $"Erreur : {ex.Message}";
        }
    }

    [RelayCommand]
    private async Task ToggleManualModeAsync()
    {
        if (!IsServerAvailable) return;
        HasError = false;
        try
        {
            await _api.SetConfigAsync("mode_manual", IsManualMode ? "1" : "0");
        }
        catch (Exception ex)
        {
            IsServerAvailable = false;
            HasError = true;
            ErrorMessage = $"Erreur : {ex.Message}";
            IsManualMode = !IsManualMode;
        }
    }

    [RelayCommand]
    private async Task ToggleVentilationAsync()
    {
        if (!IsServerAvailable) return;
        HasError = false;
        try
        {
            await _api.SetRelayAsync(IsVentilationOn);
        }
        catch (Exception ex)
        {
            IsServerAvailable = false;
            HasError = true;
            ErrorMessage = $"Erreur : {ex.Message}";
            IsVentilationOn = !IsVentilationOn;
        }
    }

    [RelayCommand(CanExecute = nameof(CanExecuteAction))]
    private async Task RebootAsync()
    {
        var confirm = await Application.Current!.Windows[0].Page!
            .DisplayAlertAsync("Redémarrage", "Voulez-vous vraiment redémarrer le Raspberry Pi ?", "Oui", "Non");

        if (!confirm) return;

        HasError = false;
        try
        {
            await _api.RebootAsync();
            await Application.Current.Windows[0].Page!
                .DisplayAlertAsync("Redémarrage", "Redémarrage en cours...", "OK");
        }
        catch (Exception)
        {
            await Application.Current.Windows[0].Page!
                .DisplayAlertAsync("Redémarrage", "Redémarrage en cours...", "OK");
        }
    }
}
