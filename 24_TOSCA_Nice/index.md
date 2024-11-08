---
title: <br><br> Shear with Radio Galaxy <br> Polarization & Kinematics
author: Cail Daley
date: Nice TOSCA Meeting <br> <br> November 8th, 2024
---

# Outline {.center}

# Motivation {.center}

In cosmic shear analyses, intrinsic galaxy shape is unknown.

- Shape noise: source of variance

    - need lots of galaxies to beat down noise

- Intrinsic alignments: source of bias

::: {.fragment}
**Estimates of intrinsic shape can mitigate both!**

- Kinematics: intrinsic position angle / ellipticity / symmetries

- Polarization: intrinsic position angle
:::


# Kinematic Lensing (KL) {.center}

## Intuitive Picture

[Hopp & Witmann (2024)](https://arxiv.org/abs/2410.00098)

![](figures/hopp&witmann_fig1a.png){.fragment .preload .current-visible}
![](figures/hopp&witmann_fig1b.png){.fragment .current-visible}
![](figures/hopp&witmann_fig2.png){.fragment width=55%}

## A Bit of History {.center}

::: {style="text-align: left"}
- [Blain et al. (2002)](https://arxiv.org/abs/astro-ph/0204138): first proposal of KL
    - ideal instruments predicted to be ALMA & SKA! <br><br>

- [Morales (2006)](https://arxiv.org/abs/astro-ph/0608494): proposed KL with HI surveys
    - relative to continuum surveys:
      -  line-to-continuum, HI $\dd N / \dd S$, low-SNR estimators <br><br>

::: {.fragment}
- [Gurri et al. (2020)](https://arxiv.org/abs/2009.10067): first KL measurement <br><br>

- [R.S. et al. (2024)](https://arxiv.org/abs/2409.08367): first detection of cluster lensing with KL <br><br>

- [Hopp & Witmann (2024):](https://arxiv.org/abs/2410.00098) model-independent KL method <br> leveraging  kinematic symmetries <br><br>
:::
:::

## First KL Measurement (Gurri et al. 2020) 

- 18 hand-picked galaxy-galaxy systems: $\ev{\gamma} = 0.0201 \pm 0.0079$ 

    - primarily sensitive to $\gamma_\times$; $\gamma_+$ degenerate with inclination and scale radius

- kinematic shape noise dominates uncertainty: <br> $\sigma_k \sim 0.03$ vs. $\sigma_p \sim 0.2$, so need $\sim$ 50 times fewer galaxies*

![](figures/gurri_etal24_figure6.png){width=75% .fragment .current-visible .preload}
![](figures/gurri_etal24_figure8.png){.fragment .current-visible}

::: {.fragment style="margin-top:180px"}
- Lower kinematic shape noise when gas & stellar velocity fields match

- Point to SKA as enabler of KL at scale!
:::

 

## KL State of the Art (R. S. et al. 2024)

- 141 target galaxies $\to$ 3 after cuts. 
- use Tully-Fisher to estimate inclination $\implies$ intrinsic ellipticity
    - $\gamma_+$ constrained via Tully-Fisher
    - $\gamma_\times$ via kinematic-photometric misalignment
- per-galaxy SNR > 1, and 10$\times$ reduction in shape noise!

![](figures/rs_etal24_fig5.png){.fragment .current-visible .preload  width=85%}

![](figures/rs_etal24_fig6.png){.fragment}

## KL Symmetries (Hopp & Witmann 2024)

![](figures/hopp&witmann_fig3.png){.fragment .current-visible .preload}
![](figures/hopp&witmann_fig13.png){.fragment}

## Almost Feasible with [WALLABY](https://wallaby-survey.org/beta-science/)? 

 21 CM H1 survey, 30" resolution, up to z=0.1

::: {.fragment .preload .current-visible}
![](figures/ASAP_WALLABy_vels1.png){width=18%} ![](figures/ASAP_WALLABy_vels2.png){width=18%}

WALLABY website, data from Serra et al. (2015)
:::

::: {.fragment}
![Murugeshan et al (2024)](figures/murugheshan_etal24_fig7.png){width=95%}
:::


## Feasible with ALMA

[The ALMA-ALPAKA survey I (Rizzo et al. 2023)](https://arxiv.org/abs/2303.16227)

high-resolution CO and [CI] kinematics of star-forming galaxies at z = 0.5-3.5


![](figures/rizzo_etal23_fig7.png)

![](figures/rizzo_etal23_fig13.png)


# Radio Galaxy Polarization  {.center}

## Intuition

- Star-forming galaxies dominate observed sources
  - synchrotron emission driven by large-scale galactic magnetic fields
    <br> $\implies$ polarization position angle 

- Nearby spiral polarization fractions: 1-10% (Stil et al. 2008)

- polarization angle not affected by lensing

  - but Faraday effect, and cosmic birefringence..

::: {.fragment style="margin-left:500px;margin-top:-150px"}
![](figures/stil_etal08_fig4.png){width=35%}
![](figures/stil_etal08_fig2.png){width=55%}

Stil et al. (2008)
:::

## Polarization: Some Examples {.scrollable}

[Slides from a presentation by David Mulcahy](https://www.mpifr-bonn.mpg.de/1281929/Beck_Galaxies.pdf)

![](figures/mulcahy_slide1.png)
![](figures/mulcahy_slide2.png)
![](figures/mulcahy_slide3.png)

**Polarized thermal emission from dust in a galaxy at redshift 2.6**
<br> [(Geach et al. 2023)](https://arxiv.org/abs/2309.02034)

:::::::::::::: {.columns}
::: {.column style="width:50%"}
![](figures/geach_etal23_data.png)
:::
::: {.column style="width:50%"}
![](figures/geach_etal23_sourceplane.png){width=75%}
:::
::::::::::::::


## A Bit of History

- Kronberg et al. 1991, Kronberg, Dyer & Roeser 1996, Burns et al. 2004:
  <br> lensing measurements with polarized radio jets

![](figures/burns_etal04.png){width=100%}

## A Bit of History

- Brown & Battye ([2011a](https://arxiv.org/abs/1005.1926), [2011b](https://arxiv.org/abs/1106.0816)): first polarization shear estimator

![](figures/brown&battye11.png){width=70%}

## A Bit of History

- Whitaker et al. ([2015](https://arxiv.org/abs/1503.00061), [2018](https://arxiv.org/abs/1702.01700)): 
  - improve upon B&B11 estimator
  - **quadratic estimator** <br>using pol. vectors combined with finite-difference gradients of Stokes I
  - estimates of rotation from birefringence: <br> 2.03º $\pm$ 0.75º (authors caution Farrady rotation systematics)

![2PCF upper limits from 30 sources](figures/whittaker_etal18.png){width=70%}

## Weak Lensing Rotation

[Thomas et al. 2016](https://arxiv.org/abs/1612.01533)

- Tensor & vector gravitational potentials allow for <br> a rotation mode $\omega$ in addition to $\gamma$ and $\kappa$:
    ![](figures/thomas_etal16_eq1.png){width=75%}

  - only measurable if source-plane position angle can be estimated<br><br>

::: {.fragment}
- Second-order effect in $\Lambda$CDM, post-Born/lens-lens coupling\

  - should be equivalent to shear $B$-modes <br> $\implies$ systematics (or $\Lambda$CDM) null test<br><br>
:::

::: {.fragment}
- Can solve simultaneously for shear and rotation from lensing
:::

  
## A new observable for cosmic shear

[Francfort, Durrer, & Cusin (2022)](https://arxiv.org/abs/2203.13634)

Estimator based on correlation function of lensing-induced rotation itself.

::: {.fragment}
**For a single galaxy:** <br>
$\alpha$ is position angle; $\delta \alpha$ is lensing-induced rotation
$$\Theta = \frac{2 - \epsilon^2}{\epsilon^2} \delta \alpha = \gamma_2 \cos 2 \alpha - \gamma_1 \sin 2 \alpha$$
:::

::: {.fragment}
**For a pair of galaxies 1,2:**
$$\Xi = \Theta(\vb n_1, \alpha_1, z_1) \Theta(\vb n_2, \alpha_2, z_2)$$
:::

::: {.fragment}
**Estimator averaging over $\Xi, \Xi'$ pairs (4-pt?):** <br>
![](figures/francfort_etal22_xi.png)
:::

<!-- # Observational Prospects {.scrollable}

[EMU](http://emu-survey.org/index.html): 10" resolution,  10-15 mJy/beam sensitivity


![ASKAP EMU Survey](figures/ASKAP_EMU_sample.png)

[Gupta et al (2024):](https://arxiv.org/abs/2403.14235) 10 414 **resolved** radio galaxies in 270 deg²

![](figures/Gupta_etal24_fig1.png)

![](figures/Gupta_etal24_fig2.png)

[POSSUM:](https://possum-survey.org) Polarization -->

# Relevance to TOSCA 


