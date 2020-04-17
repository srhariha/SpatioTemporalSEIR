---
title: A Spatio-temporal siimulator to model the likely spread of
		Covid-19 in Kerala
fontsize: 12pt
geometry: margin=2cm
---

# Aim

To build a spatio-temporal simulator that can predict the spread of Covid-19 in
Kerala under different mitigation strategies. We hope that this will be useful
for experts in community health to corroborate their intuition against a mathematical prediction. 

# Key features

1.	The resolution of the model is at the smallest local self-governing
	division (LSGD) in Kerala.  That is, grama panchayat, municipality or
	municipal corporation. 

2. 	The predictions are  based on available information about the
	characteristics of the disease, the geographic and demographic data of
	Kerala and the statistics of reported cases so far. 

3. 	The time evolution of the disease in each LSGD is modelled using a
	deterministic [SEIR model](https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#The_SEIR_model)
	fine-tuned for Covid-19.

4. 	The mixing of population between panchayats is based on the [*radiation
	law* for human mobility](https://en.wikipedia.org/wiki/Radiation_law_for_human_mobility) 

5. 	Spatio-temporal effect of various lockdown strategies can be tried out by
	the user. Some examples of lockdown strategies include
	(a) Lockdown a panchayat for $d$ days if there are more than $c$ active
		cases in that panchayat.  
	(b) Lockdown a panchayat and its neighbouring panchayats for $d$ days if
		there are more than $c$ active cases in that panchayat.

6.	A lockdown strategy will be declared as *safe* if the demand for number of
	cases needing hospitalisation is within the capacity of the corresponding
	LSGD at every point in time. Other strategies will be declared as *unsafe*.
	A quality parameter will be reported for each safe strategy tried. The
	quality parameter is equal to the average number of working days
	(non-lockdown days) per person for the next year. 

7. 	The system will automatically try out various lockdown strategies in the
	backend and provide a small set of safe strategies which acheive high
	values for the above quality parameter.

# User interface

1.	A web dashboard like [Covid19-Scenarios](https://covid19-scenarios.org/)
	with added map-based animations like
	[OurWoldInData](https://ourworldindata.org/grapher/total-covid-deaths-per-million)
	for projected data.

2. 	The user can try out the effect of various spatio-temporal lockdown
	strategies like those available in
	[CovidMeasures](https://covid-measures.github.io/)

3.	A discussion forum (not sure if it is needed or not)

4.	A logging of crowd-sourced high quality strategies (again, not sure)

# Time evolution (SEIHR Model) - Biren might update this

![SEIHR model without mixing between regions](./SEIHR.png)

The SEIHR model considers the total population $N_i$ in a region $R_i$ as being
split into five compartments based on their stage of infection. The number of
people in these five compartments is a function of time but they always add to
$N_i$. 

-	$S$ : Susceptible (before virus enters their body)
-	$E$ : Exposed (virus is multiplying inside their body but they are not
		infectious/contagious yet)
-	$I$ : Infectious
-	$H$ : Not infectious but still hospitalised
-	$R$ : Removed (recovered + dead)

The reason to add a separate category H to the standard SEIR model is to estimate the load on hospital beds. The number of hospital beds will be a function of I + H and not I alone.

## Temporal evolution equations

$$
\begin{aligned}
\dot S_i	 &= -\beta S_i \frac{I_i}{N_i} \\
\dot E_i	 &= \beta S_i \frac{I_i}{N_i} - \frac{E_i}{t_E}\\
\dot I_i	 &= \frac{E_i}{t_E} - \frac{I_i}{t_I}\\
\dot H_i	 &= \frac{I_i}{t_I} - \frac{H_i}{t_H}\\
\dot R_i	 &= \frac{H_i}{t_H}\\
\end{aligned}
$$

Here 

-	$\beta = \pi c$, where
	-	$\pi$ is the probability that a susceptible person who contacts an
		infectious person catches the disease (not all contacts transmit the
		disease)

	-	$c$ is the expected number of people that a susceptible person contacts
		in a day. Going further we will have to model it as $c = c_h + c_w$,
		where $c_h$ and $c_w$ are the expected number of people that a
		susceptible person contacts at home and work/school respectively.

	-	$c \frac{I_i}{N_i}$ therefore, is the expected number of infectious
		people that a susceptible person contacts in a day.

	-	$\pi c \frac{I_i}{N_i}$ therefore, is the probability that that a
		susceptible person catches the disease in a day.

-	$t_E$, $t_I$ and $t_R$ are the mean time that a person spends in the 
	respective compartments, before moving onto the next.

-	The time variable is hidden in the above equations for readability.
	$S_i$ should be read as $S_i(t)$ and $\dot S$ should be read as
	$S(t+1) - S(t)$, and so on.

## Current parameter choices

-	$\pi \approx 0.02$, this can reduce with the use of masks and regular
	cleansing.
-	$c_h \approx 5$
-	$c_w$ is typically 15 on a normal day and 0 on a lockdown day.
-	$t_E \approx 5$
-	$t_I \approx 5$
-	$t_H \approx 9$


# Spatial mixing (Radiation Model)

1.	We say that a person *travels* from region $R_1$ to region $R_2$, if she
	lives in $R_1$ but works mostly in $R_2$. We will assume that there are
	$r$ regions in total.

2.	**Radiation model.**
	The number of people $T_{i,j}$ travelling from region $R_i$ to region $R_j$
	on a working day is modelled as

	$$
	T_{i,j} = T_i \frac {N_i N_j}{(N_i + S_{i,j})(N_i + N_j + S_{i,j})},
	$$
	where 

	- $N_i$ is the population of $R_i$

	- $N_j$ is the population of $R_j$ 

	- $T_i$ is the total number of people who travel out for work from region
	  $R_i$.  At a larger granularity this data for each region may be available
	  from Census. Otherwise, one can model it as $T_i = \mu N_i$, pick $\mu$
	  from the census data.  The proportion of people who travel more than 5 km
	  for work may be a good proxy for $\mu$ at LSGD level (need to discuss
	  this).

	- $S_{i,j}$ is the total population in all the regions (except $R_i$ itself) 
	  which are closer to $R_i$ than $R_j$. That is,

	  $$
	  S_{i,j} = \sum_{k=1}^{r} \{N_k :~ d(R_k, R_i) \leq d(R_j, R_i)\} - N_i - N_j.
	  $$

	  It turns out that $T_i = \sum T_{i,j}$. We will also set $T_{i,i} = N_i -
	  T_i$, which can be interpretted as the number of people from region $R_i$
	  travelling to $R_i$ itself. This will make the future summations easier
	  to write.

3.	**Workplace Contact Matrix.** 
	This is an $r \times r$ matrix $C_w$ in which the entry $C_w[i,j]$ is 
	the expected number of people from region $R_j$ that a susceptible person
	from region $R_i$ will contact at workplace/school in a day. We model
	it as

	$$
	C_w[i,j] = c_w \sum_{k=1}^{r} \frac{T_{i,k}}{N_i} \frac{T_{j,k}}{\sum_{l=1}^{r} T_{l,k}}
	$$

	If you consider a person picked uniformly at random from region $R_i$, the
	term $\frac{T_{i,k}}{N_i}$ can be interpretted as the probability that she
	goes for work in region $R_k$ and the term	$\frac{T_{j,k}}{\sum_{l=1}^{r}
	T_{l,k}}$ can be interpretted as th probability that a person she contacts
	at workplace (in region $R_k$) has come to work there from region $R_j$.
	Notice that the total number of people in region $R_k$ during the day is
	not $N_k$ but $\sum_{l=1}^{r} T_{l,k}$. Since we have chosen $T_{k,k}$ as
	$N_k - T_k$, this sum will account for the people leaving and entering
	$R_k$ for work.

4.	**Contact Matrix.**
	The contact matrix $C$ is obtained by adding $c_h$ to each diagonal
	entry of $C_w$. This is justified since all household contacts happen
	in the region of a person's living.

## Current parameter choices

-	$\mu \approx 0.01$ (will update after looking at census data)

# Spatio-Temporal Evolution

$$
\begin{aligned}
\dot S_i &= -\pi S_i \sum_{j=1}^{n} C_{i,j} \frac{I_j}{N_j} \\
\dot E_i &=  \pi S_i \sum_{j=1}^{n} C_{i,j}\frac{I_j}{N_j} - \frac{E_i}{t_E} \\
\dot I_i &=	 \frac{E_i}{t_E} - \frac{I_i}{t_I}\\
\dot H_i &=	 \frac{I_i}{t_I} - \frac{H_i}{t_H}\\
\dot R_i &=  \frac{H_i}{t_H}
\end{aligned}
$$

The sum $\sum_{j=1}^{n} C_{i,j} \frac{I_j}{N_j}$ can be implemented
as a matrix-vector multiplication if that will speed up the code.

# Modelling Mitigation strategies

1.	Every lockdown strategy is a control on the matrix $C_w$. Lockdown in a
	region $R_i$ can be modelled by zeroing out the $i$-th row and column of
	$C_w$ or by scaling it down by a fraction like $0.1$ to allow for the
	essential services. A time dependent lockdown strategy will do this
	tweaking with the $C_w$ matrix differently at different time-steps.

2.	Break-the-chain campaigns like masks, hand sanitizers, social distancing
	etc are a control on $\pi$.

3. 	Effect of contact tracing and quarantining suspected contacts is difficult
	to be modelled in our setup.

4.	To model the effect of isolating symptomatic patients, we will need
	to split the compartment $I$.

# Justifying the model and parameter choices

## Radiation Model

The *radiation model* was proposed by Simini et al.[^1] in 2012 as an
alternative to the very popular gravity model. The model equation is derived
based on three assumptions, one behavioral and two economic.

1. A person who decides to travel out of her home panchayat for
   a job, travels to the nearest panchayat where she gets a job that pays more
   than the highest paying job in her own panchayat.

2. The job salaries are independent samples drawn from the same probability
   distribution. This, for example, means that the average salary is the same
   in all panchayats and salaries do not influence each other. Notice that, the
   maximum salary is still likely to be more in panchayats were there are more
   jobs.

. The number of jobs in a panchayat is proportional to the number of people
   living in that panchayat.

To paint an analogy, one can imagine every job to be a tower at the job
location whose height is the daily wage. The behavioural assumption above says
that, when a person is unsatisfied with the towers in her panchayat, she climbs
to the top of the tallest tower in her panchayat and looks all around. Among
all the towers that are taller than the one she is standing on, she chooses the
one which is at a panchayat closest to her panchayat.  That's the job she will
settle for.

One can debate on the "correctness" of the above assumptions. But the claim to
fame of a model is not its correctness but its usefulness. Studies have
compared the predictions of the model against the actual job-seeking patterns
in various places and found good fitment (add references). The feature that
makes this model most useful is that it is parameter-free and hence
"universal".  


### From assumptions to the formula.

See the appendix of Simini et al.[^1] for a derivation using continuous
probability distributions. Here we give an alternate proof using random
permutations. 

Let $N_i$ and $N_j$, respectively, be the number of jobs in panchayats $R_i$
and $R_j$. Let $d$ be the distance between $R_i$ and $R_j$. A panchayat $R_k$,
$k \neq i$, is said to be overlooked by $R_i$ in favour $of R_j$ if the
distance between $R_i$ and $R_k$ is at most $d$. Let $S_{i,j}$ be the number of
jobs that are in the panchayats overlooked by $R_i$ favour of $R_j$.  Let's
assume that a person living in panchayat $R_i$ decides to find a job
ourside $R_i$. We will show that the probability $p_{i,j}$ that she settles for
a job in panchayat $R_j$ ($j \neq i$) is 

$$
p_{i,j} = \frac {N_i N_j}{(N_i + S_{i,j})(N_i + N_j + S_{i,j})}.
$$

We have $N = N_i + N_j + S_{i,j}$ towers which are relevant for the discussion.
Let $H_i$, $H_j$ and $H_{i,j}$, respectively,  denote the maximum heights of
towers in $R_i$, $R_j$ and the panchayats overlooked by $R_i$ in favour of
$R_j$. The person settles in $R_j$ if and only if $H_{i,j} < H_i < H_j$.  Once
we notice that only the relative heights of the towers matter we can rank the
towers $1, 2, \ldots, N$ in the increasing order of their heights and then
ignore their actual heights. This ranking gives a permutation of numbers $1$ to
$n$. Assumption 2 ensures that each of the $n!$ possible permutations are
equally likely to occur. $H_j$ is larger than both $H_i$ and $H_{i,j}$ if and
only if rank $n$ falls among the $N_j$ towers in $R_j$.  Hence the probability
of this is $N_j/(N_i + N_j + S_{i,j})$. Note that this event is independent of
the relative order within the $N_i + S_{i,j}$ towers in $R_i$ and the
overlooked panchayats. Thankfully, only the relative ordering of those $N_i +
S_{i,j}$ towers determine whether $H_{i,j} < H_i$, and hence it is independent
of the previous event. $H_{i,j} < H_i$ if and only if the largest rank among
those $N_i + S_{i,j}$ towers falls among the $N_i$ towers in panchayat $R_i$.
This happens with probability $N_i/(N_i + S_{i,j})$. We get the required result
since $p_{i,j}$ is the product of the two probabilities mentioned above.

Assumption 3 helps us to replace the number of jobs in the above formula with
the number of people in each region.

## Team

- Arun Ramachandran
- Birenjith P. S.
- Deepak R.
- Sajith V. K.
- Sreeram H.



[^1]: Simini, Filippo, Marta C. González, Amos Maritan, and Albert-László
  Barabási. "[A universal model for mobility and migration patterns.][1]"
  Nature 484, no. 7392 (2012): 96-100.

[1]: https://doi.org/10.1038/nature10856

