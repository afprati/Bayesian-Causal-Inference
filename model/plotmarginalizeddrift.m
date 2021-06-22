% load one chain
for j=1:5
load("results/drift" + int2str(j) + ".mat");

tic;
% thin samples
rng('default');
skip = 1000;
thin_ind = (randi(skip, size(chain,1),1) == 1);
chain = chain(thin_ind,:);

% iterate all posterior samples
% uppers = {};
% lowers = {};
for i=1:size(chain,1)
    
    theta_0 = unwrap(theta);
    theta_0(theta_ind)=chain(i,:);
    theta_0 = rewrap(theta, theta_0);

    [mu, s2, days, counts]=drift_posterior(theta, non_drift_idx,...
        mean_function, covariance_function, x, y);
    
    mus{i} = mu;
    uppers{i} = mu+1.96*sqrt(s2./counts);
    lowers{i} = flip(mu-1.96*sqrt(s2./counts),1);
end

fig = figure(1);
clf;
f = [mean(cell2mat(uppers),2); mean(cell2mat(lowers),2)];
fill([days; flip(days,1)], f, [7 7 7]/8);
hold on; plot(days, mean(cell2mat(mus),2));

toc;

filename = "./results/marginalizeddrift"+int2str(j)+".pdf";
set(fig, 'PaperPosition', [0 0 10 10]); %Position plot at left hand corner with width 5 and height 5.
set(fig, 'PaperSize', [10 10]); %Set the paper to have width 5 and height 5.
print(fig, filename, '-dpdf','-r300');
close;

end