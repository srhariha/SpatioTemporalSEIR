---
title: A Spatio-Temporal Simulator for Spread of Covid-19 in Kerala
fontsize: 12pt
geometry: margin=2cm
---

## Aim

To build a spatio-temporal simulator that can predict the spread of Covid-19 in
Kerala under different mitigation strategies. We hope that this will be useful
for experts in community health to corroborate their intuition against a mathematical prediction. 

## Key features

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
	(a) Lockdown a panchayat for $d$ days if there are more than $c$ active cases in that panchayat.
	(b) Lockdown a panchayat and its neighbouring panchayats for $d$ days if there are more than $c$ active cases in that panchayat.

6.	A lockdown strategy will be declared as *safe* if the demand for number of
	cases needing hospitalisation is within the capacity of the corresponding
	LSGD at every point in time. Other strategies will be declared as *unsafe*.
	A quality parameter will be reported for each safe strategy tried. The
	quality parameter is equal to the average number of working days
	(non-lockdown days) per person for the next year. 

7. 	The system will automatically try out various lockdown strategies in the
	backend and provide a small set of safe strategies which acheive high
	values for the above quality parameter.

## User interface

1.	A web dashboard like [Covid19-Scenarios](https://covid19-scenarios.org/)
	with added map-based animations like
	[OurWoldInData](https://ourworldindata.org/grapher/total-covid-deaths-per-million)
	for projected data.

2. 	The user can try out the effect of various spatio-temporal lockdown
	strategies like those available in
	[CovidMeasures](https://covid-measures.github.io/)

3.	A discussion forum (not sure if it is needed or not)

4.	A logging of crowd-sourced high quality strategies (again, not sure)

## Time evolution (SEIHR Model) - Biren might update this

![SEIHR model without mixing between regions](./SEIHR.png)

The SEIHR model considers the total population $N_i$ in a region $R_i$ as being
split into five compartments based on their stage of infection. The number of
people in these five compartments is a function of time but they always add to
$N_i$. Hence for every region $R_i$, 
$$S_i(t) + E_i(t) + I_i(t) + H_i(t) + R_i(t) = N_i.$$ 

-	S : Susceptible (before virus enters their body)
-	E : Exposed (virus is multiplying inside their body but they are not
	infectious/contagious yet)
-	I : Infectious
-	H : Not infectious but still hospitalised
-	R : Removed (recovered + dead)

The reason to add a separate category H to the standard SEIR model is to estimate the load on hospital beds. The number of hospital beds will be a function of I + H and not I alone.

### Update equations

If we discretize time $t$ to represent days, then we can write the update
equations as
$$\begin{aligned}
\Delta S_i	 &= -\beta S_i \frac{I_i}{N_i} \\
\Delta E_i	 &= \beta S_i \frac{I_i}{N_i} - \frac{E_i}{t_E}\\
\Delta I_i	 &= \frac{E_i}{t_E} - \frac{I_i}{t_I}\\
\Delta H_i	 &= \frac{I_i}{t_I} - \frac{H_i}{t_H}\\
\Delta R_i	 &= \frac{H_i}{t_H}\\
\end{aligned}$$

Here 

-	$\beta = \pi c$, where
	-	$\pi$ is the probability that a susceptible person who contacts an
		infectious person catches the disease (not all contacts transmit the
		disease)

	-	$c$ is the expected number of people that a susceptible contacts in a
		day

	-	$c \frac{I_i}{N_i}$ therefore, is the expected number of infectious
		people that a susceptible person contacts in a day.

	-	$\pi c \frac{I_i}{N_i}$ therefore, is the probability that that a
		susceptible person catches the disease in a day.

-	$t_E$, $t_I$ and $t_R$ are the mean time that a person spends in the 
	respective compartments, before moving onto the next.

### Current parameter choices

-	$\pi \approx 0.02$, this can reduce with the use of masks and regular
	cleansing.
-	$\kappa$ is typically 20 on a normal day and 5 on a lockdown day.
-	$t_E \approx 5$
-	$t_I \approx 5$
-	$t_H \approx 9$


## Spatial mixing (Radiation Model)

1.	We say that a person *travels* from region $R_1$ to region $R_2$, if she
	lives in $R_1$ but works mostly in $R_2$.

2.	**Radiation model.**
	The number of people $T_{i,j}$ travelling from region $R_i$ to region $R_j$
	on a working day is modelled as
	$$ T_{i,j} = T_i \frac {N_i N_j}{(N_i + S_{i,j})(N_i + N_j + S_{i,j})},$$
	where 

	- $N_i$ is the population of $R_i$

	- $N_j$ is the population of $R_j$ 

	- $T_i$ is the total number of people who travel for work from region
	  $R_i$.  At larger granularity this data for each region may be available
	  from Census. Otherwise, one can model it as $T_i = \mu N_i$, pick $\mu$
	  from the census data.  The proportion of people who travel more than 5 km
	  for work may be a good proxy for $\mu$ at LSGD level (need to discuss
	  this).

	- $S_{i,j}$ is the total population in all the regions (except $R_i$ itself) 
	  which are closer to $R_i$ than $R_j$. That is,
	  $S_{i,j} = \sum \{N_k :~ 0 < d(R_k, R_i) < d(R_j, R_i)\}$.

	It turns out that $T_i = \sum T_{i,j}$.

3.	**Travel Rate**
	$$
		\theta_{i,j} = \frac{T_{i,j}}{N_i}
	$$
	This can be thought of as the rate at which people from region $R_i$ travel
	to region $R_i$ for work or as the probability that a person in region
	$R_i$ travels to region $R_j$ for work.

### Current parameter choices

-	$\mu \approx 0.01$ (will update after looking at census data)

## Spatio-Temporal Evolution

The following equations are adapted from Eqn (4), Section 3.1.2 in 
a [2016 paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5348083/).
This seems to miss the travel out of region $R_i$.
$$
\begin{aligned}
	\Delta S_i &= 	- \beta S_i \frac{I_i}{N_i} 
					+ \sum_j \theta_{j,i}S_j \\
	\Delta E_i &=     \beta S_i \frac{I_i}{N_i}
					- \frac{E_i}{t_E} 
					+ \sum_j \theta_{j,i}E_j \\
	\Delta I_i &=	  \frac{E_i}{t_E} 
					- \frac{I_i}{t_I} 
					+ \sum_j \theta_{j,i}I_j \\
	\Delta R_i &=     \frac{I_i}{t_I} 
					+ \sum_j \theta_{j,i}R_j
\end{aligned}
$$


## Mitigation strategies

## Justifying the model and parameter choices

## Team

- Arun Ramachandran
- Birenjith P. S.
- Deepak R.
- Sajith V. K.
- Sreeram H.
