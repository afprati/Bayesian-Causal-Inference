import torch
import gpytorch
from matplotlib import pyplot as plt


# Define plotting function
def ax_plot(ax, test_t, X, Y, m, lower, upper, LABEL):
     for i in range(2):
          ax[i].plot(1+X[i, :,-1].detach().numpy(), Y[i,:].detach().numpy(),\
          color='grey', alpha=0.8, label=LABEL)
          ax[i].plot(1+test_t.detach().numpy(), m[i].detach().numpy(),\
               'k--', linewidth=1.0, label='Estimated Y(0)')
          ax[i].fill_between(1+test_t.detach().numpy(), lower[i].detach().numpy(),\
               upper[i].detach().numpy(), alpha=0.5)
          ax[i].legend(loc=2)
          ax[i].set_title("{} Unit {}".format(LABEL, i+1))


def visualize(test_t, X_tr, Y_tr, m_tr, lower_tr, upper_tr, X_co, Y_co, m_co, lower_co, upper_co, ATT, T0):
     # Plot unit-level treatment effect
    f, axs = plt.subplots(2, 2, figsize=(12, 6))

    N_tr, T= list(Y_tr.shape)
    N_co = list(X_co.shape)[0]
    d = list(X_tr.shape)[2] - 1

    ax_plot(axs[0], test_t, X_tr, Y_tr, m_tr, lower_tr, upper_tr, "Treated")
    ax_plot(axs[1], test_t, X_co, Y_co, m_co, lower_co, upper_co, "Control")

    for i in range(2):
        for j in range(2):
             axs[i][j].axvline(x=T0, color='red', linewidth=1.0)
    plt.savefig("results/units.png")
    plt.show()


    # Plot group-level treatment effect
    # Initialize plots
    f, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))

    ax1.plot(1+test_t.detach().numpy(), torch.mean(Y_tr, dim=0).detach().numpy(), 'k', linewidth=1.0, label='Treated Averaged')

    # Averaged predictive mean
    ax1.plot(1+test_t.detach().numpy(), torch.mean(m_tr, dim=0).detach().numpy(), 'k--', linewidth=1.0, label='Estimated Y(0) Average for the Treated')

    for i in range(N_tr):
        # Plot training data 
        ax1.plot(1+X_tr[i,:,-1].detach().numpy(), Y_tr[i,:].detach().numpy(),\
             color='grey', alpha=0.8, label='Treated' if i==0 else None)
    
    for i in range(N_co):
        # Plot training data 
        ax1.plot(1+X_co[i,:,-1].detach().numpy(), Y_co[i,:].detach().numpy(),\
             color='grey', alpha=0.2, label='Control' if i==0 else None)
    
    # Treatment Time
    ax1.axvline(x=T0, color='red', linewidth=1.0)

    ax1.legend(loc=0)

    # Estimated ATT
    ax2.plot(1+test_t.detach().numpy(), torch.mean(Y_tr, dim=0).detach().numpy() - torch.mean(m_tr, dim=0).detach().numpy(),\
         'k', linewidth=1.0, label='Estimated ATT')
        
    # True ATT
    ax2.plot(1+test_t.detach().numpy(), torch.mean(ATT, dim=0).detach().numpy(), 'k--', linewidth=1.0, label='True ATT')

    # Shaded area for critical interval
    ax2.fill_between(1+test_t.detach().numpy(), torch.mean(Y_tr, dim=0).detach().numpy() - torch.mean(upper_tr, dim=0).detach().numpy(),\
         torch.mean(Y_tr, dim=0).detach().numpy() - torch.mean(lower_tr, dim=0).detach().numpy(), alpha=0.5, label="95% Critical Interval")

    ax2.axvline(x=T0, color='red', linewidth=1.0)
    ax2.legend(loc=0)

    plt.savefig("results/synthetic.png")
    plt.show()


def visualize_multitask(X_tr, X_co, Y_tr, Y_co, ATT, model, likelihood, T0):
    # Set into eval mode
    model.eval()
    likelihood.eval()

    N_tr, T= list(Y_tr.shape)
    N_co = list(X_co.shape)[0]
    d = list(X_tr.shape)[2] - 1

    test_x_tr = X_tr.reshape(-1,d+1)
    test_x_co = X_co.reshape(-1,d+1)
    test_y_tr = Y_tr.reshape(-1)
    test_y_co = Y_co.reshape(-1)
    test_t = X_tr[0,:,-1] # torch.arange(T, dtype=torch.float)

    test_i_tr = torch.full_like(test_y_tr, dtype=torch.long, fill_value=0)
    test_i_co = torch.full_like(test_y_co, dtype=torch.long, fill_value=1)    

    # Make predictions
    with torch.no_grad(), gpytorch.settings.fast_pred_var():
         f_pred_tr = model(test_x_tr, test_i_tr)
         f_pred_co = model(test_x_co, test_i_co)

    # Get lower and upper confidence bounds
    lower_tr = f_pred_tr.mean - 1.92*torch.sqrt(f_pred_tr.variance)
    upper_tr = f_pred_tr.mean + 1.92*torch.sqrt(f_pred_tr.variance)
    m_tr = f_pred_tr.mean.reshape(N_tr, T)
    lower_tr = lower_tr.reshape(N_tr, T)
    upper_tr = upper_tr.reshape(N_tr, T)

    lower_co = f_pred_co.mean - 1.92*torch.sqrt(f_pred_co.variance)
    upper_co = f_pred_co.mean + 1.92*torch.sqrt(f_pred_co.variance)
    m_co = f_pred_co.mean.reshape(N_co, T)
    lower_co = lower_co.reshape(N_co, T)
    upper_co = upper_co.reshape(N_co, T)

    visualize(test_t, X_tr, Y_tr, m_tr, lower_tr, upper_tr, X_co, Y_co, m_co, lower_co, upper_co, ATT, T0)
