## Is this real data? If not, then what?

*Absolutely Not.* We are only showing the *projections* from a simulator which
is based on two standard mathematical models. The SEIR model for epidemic time
evolution and the Gravity Model for movement of people between regions for
daily work. Once the user enters the seed data (her guess on the number of
infectious people in each region on Day-0), and selects the mitigation
strategies to enforce, we run the simulator and show the predicted number
of infectious people (the I in the SEIR model) in each region.  The numbers are
indicated by a colour scale in the map.

## Where can I see real data?

One good place to see regularly updated real data on the Covid 19 situation in Kerala is <https://covid19kerala.info>.

## Do you use any real data at all?

*Yes*. We use the population and area of each LSG (from 2011 census data) and
the pairwise aerial distance between LSGs (extracted from GIS maps).  We also
make an indirect use of the statistics on daily commute distance of
non-agricultural workers in Kerala (from 2011 census data).

## Do you use any patient data?

*No.* The simulator runs based on the intital seed given by the user.

## What are the factors which influence the projections?

The simulator's output is heavily dependent on the model parameters, the
mitigation strategies and the initial seed of region-wise infectious people.

## What exactly are you projecting?

We are projecting the future number of Covid-19 infectious people in each grama
panchayath, municipality and municpal corporation in Kerala. 

We say that a person is *infectious* if she can potentially infect another
person through contact. The person may or may not be showing symptoms during
this stage. Even those who show symptoms are not infectious towards the later
stages of the infection. 

Currently, we are not projecting the number of positive cases or the number of
people who might require hospitalisation. We can modify the SEIR model to do
these projections also. We might do that in the future releases.

## Will these projections come true?

*No.*

## How can you be so sure?

There are multiple projections but only one truth. So surely not all these projections can be true. 

## Then what's the use of this simulator?

1.	If you are a policy maker or an expert in community health (which we are
	not) from Kerala, then you may already have an intution on how Covid-19
	will spread in Kerala under various scenarios. You can use this simulator
	to test your intution against a mathematical projection. This portal is
	developed mainly for you.  If you need any help with running the simulator
	with complex initial seeds and mitigation strategies, feel free to [contact
	us](./about-us.md).
	
2.	If you are an academician with a recent (that's some of us :) or a long
	standing interest in epidemiology, then we hope this simulator may be
	useful for you as a research tool.  The advanced controls in the portal are
	designed to give you complete control of the simulator. The only thing you
	will not be able change from the portal are the underlying models
	themselves.  For that, you are free to fork and modify [the source
	code](https://github.com/srhariha/SpatioTemporalSEIR). We hope that you
	will make those better simulators available to the first group.

3.	If you are neither of the above, you can use this portal to build your
	intution on the effectiveness of various mitigation strategies and the
	dangers of violating them. We have also created a few sample scenarios
	to get you started.

## Do you consider the effect of people coming from outside Kerala?

*Not yet*. This is the highest priority item in our to-do list. We will try to
model this based on the quarantine policies that will be put in place by the
state government this week.

## Why is it slow?

We start running the simulator only after the visitor enters the seed and
mitigations. This has to be done separately for each visitor to our portal.  We
are working on optimising the code and upgrading our server to make this
faster.

## Can I see the code behind the simulator?

*Yes*, you are most welcome to fork and improve our
[git-repo](https://github.com/srhariha/SpatioTemporalSEIR).

## Can I see the math behind the code?

*Yes*, you are most welcome to read the [mathematical description of our model](./model.md)

