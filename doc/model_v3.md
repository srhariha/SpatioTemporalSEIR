# Timeline of the virus and the SEIR Model

![SARS-CoV-2 Timeline](./Timeline.png)

A person gets infected by SARS-CoV-2 (Covid-19) virus when she comes in contact
(either directly or via a shared surface) with an infectious person. A fraction
of such people will start showing symptoms within 2 to 14 days (average 5.2
days) and the symptoms will typically last for around 10 days. This is called
as the *health timeline* in the figure below. But what matters more for
modelling is the *infectivity timeline*, which is the period during which an
infected person is infectious or contagious. This period is estimated to start
typically from about 1 to 2 days before the onset of symptoms and lasts
typically for about 6 days. This period is marked as $I$ (Infectious) in the
infectivity timeline. The period before that, starting from the day of contact
is marked as $E$ (Exposed or Latent). This is when the virus is multiplying in
her body but is still not numerous enough to be infectious. The period after
$I$ is marked as $R$ (Removed). This is when she is no longer infectious. She
might still have symptoms at this stage and will typically take another 8 or
more days to be cured. Note that the word "typically" is intentionally overused
in this paragraph. All these timelines vary from person to person depending on
their health conditions and viral load transmitted at contact. 

The SEIR model of disease spread is based on the infectivity timeline above.
It considers the total population $N$ in a region as being split
into four compartments based on their stage of infection. The number of people
in each compartment change with time but they always add to $N$.


![SEIR model without mixing between regions](./SEIR.png)

The time evolution of the sizes of these four compartments is modelled by
the following four ordinary differential equations.

$$
\begin{aligned}
\dot S	 &= -\beta S \frac{I}{N} \\
\dot E	 &= \beta S \frac{I}{N} - \frac{E}{t_E}\\
\dot I	 &= \frac{E}{t_E} - \frac{I}{t_I}\\
\dot R	 &= \frac{I}{t_I}
\end{aligned}
$$

Here 

-	$\beta = p c$, where
	-	$p$ is the probability that a susceptible person who contacts an
		infectious person catches the disease (not all contacts transmit the
		disease)

	-	$c$ is the expected number of people that a susceptible person contacts
		in a day. Going further we will have to model it as $c = c_h + c_w$,
		where $c_h$ and $c_w$ are the expected number of people that a
		susceptible person contacts at home and work/school respectively.

	-	$c \frac{I}{N}$ therefore, is the expected number of infectious
		people that a susceptible person contacts in a day.

	-	$p c \frac{I}{N}$ therefore, is the probability that that a
		susceptible person catches the disease in a day.

-	$t_E$ and $t_I$ are the mean time that a person spends in
	the respective compartments, before moving onto the next.

- 	The time variable is hidden in the above equations for readability. For
	example,  $S$ should be read as $S(t)$ and $\dot S$ should be read as
	$\frac{d}{dt}S(t)$.  




# Spatial mixing 

We say that a person *travels* from region $R_i$ to region $R_j$, if she lives
in $R_i$ but goes daily to $R_j$ for work. We will assume that there are $r$
regions in total. Let us denote by $T_{i,j}$, the number of people travelling
for work from region $R_i$ to region $R_j$ in a day. How fast an epidemic
spreads over various regions depends mainly on these numbers. Unfortunately, we
do not have actual estimates for these numbers. Hence we use a commonly used
mathematical model called the *gravity model* to artificially estimate  these
numbers.

## Travel matrix $T$ from Gravity model

The gravity model needs three inputs, some of which we indirectly modelled
using the population statistics. We denote the population of region $R_i$ with
$N_i$.

1.	$T_i$, the number of people who travel out from region $R_i$ every day. We
	need this for for every LSGD in the state. In the absence of direct
	estimates, we assume $T_i$ indirectly from the 2011 census data as follows.

	Census 2011 contains a histogram of daily travel distances of
	non-agricultural workers at district level resolution. Since the histogram
	is coarse and there is no huge variation across districts, we estimate
	$T_i$ as $T_i = \mu N_i$, where 
  	-	$\mu = 0.09$ for regions with area less than $25$ square kilometers
	-	$\mu = 0.04$ for regions with area between $25$ and $100$ square
		kilometers
	-	$\mu = 0.02$ for regions with area more than $100$ square kilometers

	The values 9%, 4% and 2% used above are based, respectively, on the 2011
	census estimate of the percentage of population travelling more than $5$,
	$10$ and $20$ kilometers for work (Kerala overall statistics).


2. 	$J_j$ is the number of non-agricultural job opportunities in $R_j$. We need
	this too for every LSGD. It will be great if one can find these numbers
	from a primary source. In the absence of such a source, we model it as $J_j
	= \zeta N_j$, where 
	- $\zeta = 0.1$ for grama panchayats,
	- $\zeta = 0.2$ for municipalities and 
	- $\zeta = 0.3$ for corporations

	*Notes.* Only the relative magnitudes of the three zeta's matter. We
	consider only non-agricultural jobs, since census data considers that
	agricultural sector jobs has very little contribution to long-distance
	(more than 5 km) daily commuting.

3.	$d_{i,j}$ is the travel distance between regions $R_i$ and $R_j$. We need
	this for every pair of LSGDs.

Using these three inputs, we model the number of people $T_{i,j}$ travelling
for work from region $R_i$ to region $R_j$ in a day is as

$$
T_{i,j} = \alpha_i \frac {T_i J_j}{d_{i,j}^2}.
$$
where the normalisation factor 
$$
\alpha_i = \left(\sum_{k \neq i}(J_k/d_{i,k}^2)\right)^{-1}.
$$

We assume the dependence on the distance to be $T_{i,j} \propto 1/d_{i,j}^2$.
This dependence is usually calibrated based on real data of job movement in a
region. In the absence of such data for Kerala, we are making an arbitrary
choice here based on a subjective validation of the results.

Putting it all together in one formula, we get

$$
T_{i,j} = T_i \frac{(J_j/d_{i,j}^2)}{\sum_{k \neq i}(J_k/d_{i,k}^2)},~ \forall j \neq i,
$$
and then compute $T_{i,i} = N_i - \sum_{k \neq i} T_{i,k}$. Theoretically
$T_{i,i}$ should be $N_i - T_i$, but it may have rounding errors.

##	Normal Workplace Contact matrix $W_N$

The *Normal Workplace Contact Matrix* $W_N$ is an $r \times r$ matrix in which
the entry $W_N[i,j]$ is the expected number of people from region $R_j$ that a
susceptible person from region $R_i$ will contact at workplace/school during a
*normal day*. We will scale this matrix appropriately for non-normal days, that
is days in which any mitigation strategy is active. We model $W_N$ as a
function of the population statistics and the travel matrix.

$$
W_N[i,j] = c_w \sum_{k=1}^{r} \frac{T_{i,k}}{N_i} \frac{T_{j,k}}{\sum_{l=1}^{r} T_{l,k}},
$$
where

-	$c_w$ is the expected number of people that a susceptible person contacts
	at work/school on a normal day,

-	$N_i$ is the population of region $R_i$, and

-	$T_{i,j}$ is the expected number of people travelling for work from region
	$R_i$ to region $R_j$ on a normal day.


*Justification.* If we consider a person picked uniformly at random from region
$R_i$, the term $T_{i,k} / N_i$ can be interpreted as the probability that she
goes for work in region $R_k$ and the term $T_{j,k} / \sum_{l=1}^{r} T_{l,k}$
can be interpreted as the probability that a person she contacts at workplace
(while at work in region $R_k$) has come to work there from region $R_j$.
Notice that the total number of people in region $R_k$ during the day is not
$N_k$ but $\sum_{l=1}^{r} T_{l,k}$. Since we have chosen $T_{k,k}$ as $N_k -
T_k$, this sum will automatically account for the people who live and work in
$R_k$.

## Mitigated Workplace Contact Matrix $W_M$

The *mitigated workplace contact matrix* $W_M$ is a function of the normal
workplace contact matrix $W_N$ and the various mitigation strategies like
break-the-chain, lockdowns, hotspots etc that are active in the state on a day.
The entry $W_M[i,j]$ will represent the expected number of people from region
$R_j$ that a susceptible person from region $R_i$ will contact at
workplace/school during a day when all the active mitigation strategies are in
place.

This matrix will have to be recomputed whenever there is a change in mitigation
strategies. The reduction in workplace contact rate due to each mitigation
strategy is captured either by a single number or an $r$-length array as given
below. 

1.	Break the Chain
	- A single number $\epsilon_{BC}$ .

2.	Complete Lockdown 
	- A single number $\epsilon_{LD}$ .

3.	District Border Closure
	- A single number $\epsilon_{LD}$ and a static $r \times r$ interdistict
	  matrix $X_{DB}$.

	- $X_{DB}[i,j] = 0$ if $R_i$ and $R_j$ are in the same district
	- $X_{DB}[i,j] = 1$ if $R_i$ and $R_j$ are in different districts

	- In a seven-region toy example with regions 1 and 2 in the first district,
	  regions 3, 4 and 5 in the second district and regions 6 and 7 in the
	  third, the $X_{DB}$ matrix will look like
	  $$
	  \begin{bmatrix}
	  0 & 0 & 1 & 1 & 1  & 1 & 1 \\
	  0 & 0 & 1 & 1 & 1  & 1 & 1 \\
	  1 & 1 & 0 & 0 & 0  & 1 & 1 \\
	  1 & 1 & 0 & 0 & 0  & 1 & 1 \\
	  1 & 1 & 0 & 0 & 0  & 1 & 1 \\
	  1 & 1 & 1 & 1 & 1 & 0 & 0 \\
	  1 & 1 & 1 & 1 & 1 & 0 & 0 
	  \end{bmatrix}
	  $$

4.	Hotspots
	- $M_{HS}[i,j] = \epsilon_{HS}$ if either $R_i$ or $R_j$ is a hotspot.
	  Otherwise it is $1$.
	- In the seven-region toy example with regions 2,3 and 7 declared as
	  hotspots, $M_{HS}$ matrix will look like
	  $$
	  \begin{bmatrix}
	  1 & \epsilon_{HS} & \epsilon_{HS} & 1 & 1 & 1 & \epsilon_{HS} \\
	  \epsilon_{HS} & \epsilon_{HS}  & \epsilon_{HS} & \epsilon_{HS} & \epsilon_{HS}  & \epsilon_{HS} & \epsilon_{HS} \\
	  \epsilon_{HS} & \epsilon_{HS}  & \epsilon_{HS} & \epsilon_{HS} & \epsilon_{HS}  & \epsilon_{HS} & \epsilon_{HS} \\
	  1 & \epsilon_{HS} & \epsilon_{HS} & 1 & 1 & 1 & \epsilon_{HS} \\
	  1 & \epsilon_{HS} & \epsilon_{HS} & 1 & 1 & 1 & \epsilon_{HS} \\
	  1 & \epsilon_{HS} & \epsilon_{HS} & 1 & 1 & 1 & \epsilon_{HS} \\
	  \epsilon_{HS} & \epsilon_{HS}  & \epsilon_{HS} & \epsilon_{HS} & \epsilon_{HS}  & \epsilon_{HS} & \epsilon_{HS} 
	  \end{bmatrix}
	  $$
	- *Inputs* : Date ranges and list of hotspots

5.	 Red and Orange Zones
	- $M_{RZ}[i,j] = \epsilon_{RZ}$ if either $R_i$ or $R_j$ is in a red zone
	  district.  Otherwise it is $1$.
	- In the seven-region toy example with distict-2 (regions 3,4 and 5)
	  declared as red zone, $M_{RZ}$ matrix will look like
	  $$
	  \begin{bmatrix}
	  1 & 1 & \epsilon_{RZ} & \epsilon_{RZ} & \epsilon_{RZ} & 1 & 1 \\
	  1 & 1 & \epsilon_{RZ} & \epsilon_{RZ} & \epsilon_{RZ} & 1 & 1 \\
	  \epsilon_{RZ} & \epsilon_{RZ}  & \epsilon_{RZ} & \epsilon_{RZ} & \epsilon_{RZ}  & \epsilon_{RZ} & \epsilon_{RZ} \\
	  \epsilon_{RZ} & \epsilon_{RZ}  & \epsilon_{RZ} & \epsilon_{RZ} & \epsilon_{RZ}  & \epsilon_{RZ} & \epsilon_{RZ} \\
	  \epsilon_{RZ} & \epsilon_{RZ}  & \epsilon_{RZ} & \epsilon_{RZ} & \epsilon_{RZ}  & \epsilon_{RZ} & \epsilon_{RZ} \\
	  1 & 1 & \epsilon_{RZ} & \epsilon_{RZ} & \epsilon_{RZ} & 1 & 1 \\
	  1 & 1 & \epsilon_{RZ} & \epsilon_{RZ} & \epsilon_{RZ} & 1 & 1
	  \end{bmatrix}
	  $$
	- *Inputs* : Date ranges and list of LSGDs under red zone \
	- Orange zone is similar to red zone, but with a different $\epsilon$

Let $D$ be the number of days for which we run the simulation. Since the we
allow for a date-range to be chosen for applying each mitigaion, we will store
this information in a $D$-length array for each mitigation $MT$ ($MT$ can be
$BC$, $HS$, etc). That is,  $d_{MT}$ is a $D$-length array which contains $1$
on all days in which the mitigation strategy $MT$ is enabled and $0$ on other
days. It will be an all-zeros array if the mitigation strategy $MT$ not chosen
at all. The $days_{MT}$ array can be computed outside the main loop for simple
mitigation strategies like break-the-chain, complete lockdown and district
border closure using the corresponding date ranges. But this array will have to
be updated inside the main loop for dynamic hotspots and zones.

The effective mitigation matrix $M$ for a day $d$ is obtained as follows;

- First we obtain region specific mitigation factors array for day $d$ as
  $$
  m_R = 1 - \max\{(
  d_{LD}[d](1 - \epsilon_{LD}), 
  d_{HS}[d](1 - \epsilon_{HS}), 
  d_{RZ}[d](1 - \epsilon_{RZ}), 
  d_{OZ}[d](1 - \epsilon_{OZ})\}
  $$

- Notice that the first term inside the maximisation is a number while the rest
  are $r$-length arrays. Hence the result $m_R$ is an $r$-length array.

- The inter-district mitigation matrix $M_X$ is computed as 
  $$
  M_X = 1 - d_{DB}[d] (1 - \epsilon_{DB}) X_{DB}
  $$

- Now we combine the region-wise arrays with $M_X$
  $$
  M_{RX} = \min(\min(m_R. M), m_R^T).
  $$

- The final mitigation matrix $M$ is then obtained by applying the break-the-chain
  factor
  $$
  M = (1 - d_{BC}[d] (1 - \epsilon_{BC})) M_{RX}.
  $$

- The mitigated workplace contact matrix is obtained by **pointwise
  multiplying** $M$ and $W_N$.

## Effective Contact Matrix $C$

The *Effective Contact Matrix* $C$ is obtained from the mitigated workplace
contact matrix $W_M$ by adding expected number of daily household contacts
$c_h$ to each diagonal entry of $W_M$. This is justified since all household
contacts happen in the region of a person's living.

$$
\begin{aligned}
C[i,j] &= W_M[i,j], i \neq j, \\
C[i,i] &= W_M[i,i] + c_h.
\end{aligned}
$$

# Putting it all together - Spatio-Temporal Evolution

Finally we put all these together to form a four ordinary differential
equations per region. The first two equations for each region contain terms
from other regions too.

$$
\begin{aligned}
\dot S_i &= -p S_i \sum_{j=1}^{n} C_{i,j} \frac{I_j}{N_j} \\
\dot E_i &=  p S_i \sum_{j=1}^{n} C_{i,j}\frac{I_j}{N_j} - \frac{E_i}{t_E} \\
\dot I_i &=	 \frac{E_i}{t_E} - \frac{I_i}{t_I}\\
\dot R_i &=	 \frac{I_i}{t_I}
\end{aligned}
$$

See below the time evolution equations of the SEIR model for a description of
the variables used.  In the simulator we discretise the above by assuming that
time advances in steps of one day, and hence treat $\dot S_i$ as the daily
increment to $S_i$. That is,  $\dot S_i = S_i(t+1) - S_i(t)$. Our simulator
starts with the initial states of each variable, $S_i(0)$ , $E_i(0)$, $I_i(0)$
and $R_i(0)$ and then updates it according to the above increment rules.

# Initialisation

Currently we are doing a very simple initialisation by adding the seed numbers
of infectious people entered by the user directly to Compartment $I$ and
keeping the $E$ and $R$ compartments empty. While this is a natural thing to do
in a simulator, we remark that this is not a very realistic scenario once the
epidemic has started spreading.


# Default parameter values

## SEIR model

Parameter  | Value       | Description
---------: | :------     | :----
$p$        | 0.02        | Probability of infection per contact
$c_h$      | 5	persons  | Mean contacts per day in households
$c_w$      | 15 persons  | Mean contacts per day in workplace
$t_E$      | 3 days      | Mean latent period
$t_I$      | 6 days      | Mean latent period

## Gravity Model

Currently these parameters cannot be changed for the simulator. This is because
we pre-compute and store the travel matrix to save a lot of repeated computation.

 Parameter  Value       Description
----------  ------      ------------
$\eta$      2           Distance exponent in Gravity model
$A_S$       25 sq.km.   Area up to which an LSG is treated as small
$A_L$       100 sq.km.  Area above which an LSG is treated as large
$\mu_S$     0.09        Fraction of population who travel out for work
		   			    from a small LSG
$\mu_M$     0.04        Fraction of population who travel out for work
						from a medium LSG
$\mu_L$     0.02        Fraction of population who travel out for work
						from a large LSG
$\zeta_P$   0.1         Jobs per person in a panchayath
$\zeta_M$   0.2         Jobs per person in a municipality
$\zeta_C$   0.3         Jobs per person in a corporation

## Mitigation effects

These are the ratio by which we multiply the relevant entries in the
contact matrix when each of the mitigation strategies is active. If more than one multiplier apply to an entry, we take the minimum of those multipliers.

Multiplier      | Value   | Mitigation strategy
---------:      | :------ | :----
$\epsilon_{BC}$ | 2/3     | Break-the-chain
$\epsilon_{LD}$ | 1/3     | Complete Lockdown
$\epsilon_{DB}$ | 1/3     | District Border Closure
$\epsilon_{RZ}$ | 1/3     | Red Zone
$\epsilon_{OZ}$ | 1/3     | Orange Zone
$\epsilon_{HS}$ | 1/4     | Hotspot

