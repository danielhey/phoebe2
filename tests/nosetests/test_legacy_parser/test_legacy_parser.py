import phoebe as phb2
try:
    import phoebe_legacy as phb1
except ImportError:
    import phoebeBackend as phb1
import numpy as np
import matplotlib.pyplot as plt
import os

# phb2.devel_on()

def legacy_test(filename='default.phoebe', verbose=False):

    # load phoebe 1 file

    dir = os.path.dirname(os.path.realpath(__file__))

    phb1.init()
    if hasattr(phb1, 'auto_configure'):
        # then phb1 is phoebe_legacy
        phb1.auto_configure()
    else:
        # then phb1 is phoebeBackend
        phb1.configure()
    phb1.open(os.path.join(dir, filename))

    #load phoebe2 file
    b = phb2.Bundle.from_legacy(os.path.join(dir, filename), add_compute_legacy=True)
    b.rename_component('primary', 'cow')
    b.rename_component('secondary', 'pig')
    # create time array and get datasets


    per = b['period@orbit'].value

#    time_rv = np.linspace(0, per, 4)
#    time_lc = np.linspace(0, per, 100)


    lcs = b.get_dataset(kind='lc').datasets
    lcs = lcs[::-1]
    rvs = b.get_dataset(kind='rv').datasets
    rvs = rvs[::-1]
    print rvs
    # phb2 compute

    fluxes = []
    vels = []
    vels2 = []

    for x in range(len(lcs)):
        # load file
        datafile = phb1.getpar('phoebe_lc_filename', x)
        data = np.loadtxt(os.path.join(dir, datafile))
        time = b.filter(dataset=lcs[x], qualifier='times').get_value()
        # get third column value
        err_val = phb1.getpar('phoebe_lc_indweight', x)
        print("checking time in "+str(lcs[x]))
        assert(np.all(time==data[:,0]))
        flux = b.filter(dataset=lcs[x], qualifier='fluxes').get_value()
        if verbose: print("checking flux in "+str(lcs[x]))
        assert(np.all(flux==data[:,1]))
        sigma = b.filter(dataset=lcs[x], qualifier='sigmas').get_value()
        if verbose: print("checking sigma in "+str(lcs[x]))

        if err_val == 'Standard deviation':
            assert(np.all(sigma==data[:,2]))
        else:
            val = np.sqrt(1/data[:,2])
            assert(np.allclose(sigma, val, atol=1e-7))
        #calculate lc
        flux, mesh = phb1.lc(tuple(data[:,0].tolist()), x, 1)
        fluxes.append(flux)
        #check ld coeffs
        ldx1, ldy1 = b.filter(dataset=lcs[x], qualifier='ld_coeffs', component='cow').get_value()

        ld_coeffs1 =[phb1.getpar('phoebe_ld_lcx1', x), phb1.getpar('phoebe_ld_lcy1', x), phb1.getpar('phoebe_ld_lcx2', x), phb1.getpar('phoebe_ld_lcy2', x)]
        ldx1, ldy1 = b.filter(dataset=lcs[x], qualifier='ld_coeffs', component='cow').get_value()
        ldx2, ldy2 = b.filter(dataset=lcs[x], qualifier='ld_coeffs', component='pig').get_value()
        ld_coeffs2 = [ldx1, ldy1, ldx2, ldy2]
        if verbose: print("checking ld coeffs in "+str(lcs[x]))
        assert(np.all(ld_coeffs1==ld_coeffs2))

    rvno = phb1.getpar('phoebe_rvno')
    prim = 0
    sec = 0
    for x in range(rvno):
        if verbose: print 'rvs'
        err_val = phb1.getpar('phoebe_rv_indweight', x)
        comp = phb1.getpar('phoebe_rv_dep', x).split(' ')[0].lower()
        id = phb1.getpar('phoebe_rv_id', x)
        print "id", id
        if comp == 'primary':
            comp_name = 'cow'
        elif comp == 'secondary':
            comp_name = 'pig'
        a = int(x/2.)
        if verbose: print a
        datafile = phb1.getpar('phoebe_rv_filename', x)
        data = np.loadtxt(os.path.join(dir, datafile))
        time = b.filter(dataset=id, qualifier='times', component=comp_name).get_value()
        if verbose: print("checking time in "+str(rvs[a]))
        assert(np.all(time==data[:,0]))
        rv = b.filter(dataset=id, qualifier='rvs', component=comp_name).get_value()
        if verbose: print("checking rv in "+str(rvs[a]))
        assert(np.all(rv==data[:,1]))
        sigma = b.filter(dataset=id, qualifier='sigmas', component=comp_name).get_value()
        if verbose: print("checking sigma in "+str(rvs[a]))

        if err_val == 'Standard deviation':
            assert(np.all(sigma==data[:,2]))
        else:
            val = np.sqrt(1/data[:,2])
            assert(np.allclose(sigma, val, atol=1e-7))

        if comp_name == 'cow':

            rv1 = np.array(phb1.rv1(tuple(data[:,0].tolist()), prim))
            vels.append(rv1)
            ld_coeffs1 =[phb1.getpar('phoebe_ld_rvx1', prim), phb1.getpar('phoebe_ld_rvy1', prim), phb1.getpar('phoebe_ld_rvx2', prim), phb1.getpar('phoebe_ld_rvy2', prim)]
            ldx1, ldy1 = b.filter(dataset=id, qualifier='ld_coeffs', component='cow').get_value()
            ldx2, ldy2 = b.filter(dataset=id, qualifier='ld_coeffs', component='pig').get_value()
            ld_coeffs2 = [ldx1, ldy1, ldx2, ldy2]
            if verbose:
                print("checking ld coeffs in primary "+str(rvs[a]))
            assert(np.all(ld_coeffs1==ld_coeffs2))
            prim = prim+1
        else:
            rv2 = np.array(phb1.rv2(tuple(data[:,0].tolist()), sec))
            vels2.append(rv2)

            ld_coeffs1 =[phb1.getpar('phoebe_ld_rvx1', sec), phb1.getpar('phoebe_ld_rvy1', sec), phb1.getpar('phoebe_ld_rvx2', sec), phb1.getpar('phoebe_ld_rvy2', sec)]
            ldx1, ldy1 = b.filter(dataset=id, qualifier='ld_coeffs', component='cow').get_value()
            ldx2, ldy2 = b.filter(dataset=id, qualifier='ld_coeffs', component='pig').get_value()
            ld_coeffs2 = [ldx1, ldy1, ldx2, ldy2]
            if verbose:
                print("checking ld coeffs in secondary "+str(rvs[a]))
            assert(np.all(ld_coeffs1==ld_coeffs2))
            sec = sec+1

    b.run_compute(kind='legacy')
    for x in range(len(lcs)):
        lc2 = b.filter('fluxes', context='model', dataset=lcs[x]).get_value()
        time = b.filter('times', context='model', dataset=lcs[x]).get_value()
        if verbose: print("comparing lightcurve "+str(lcs[x]))

        assert(np.allclose(fluxes[x], lc2, atol=1e-5))

    for x in range(rvno):
        prim = 0
        sec = 0
        comp = phb1.getpar('phoebe_rv_dep', x).split(' ')[0].lower()
        if comp == 'primary':
            comp_name = 'cow'
        elif comp == 'secondary':
            comp_name = 'pig'
        rv2 = b.filter('rvs', component=comp_name, context='model').get_value()
        time = b.filter('times', component=comp_name, context='model').get_value()
        a = int(x/2.)
        if comp_name == 'cow':
            if verbose:
                print("trying primary rv at "+str(rvs[a]))
            assert(np.allclose(vels[prim], rv2, atol=1e-5))
            prim= prim+1

        else:
            if verbose:
                print("trying secondary rv at "+str(rvs[a]))
            assert(np.allclose(vels2[sec], rv2, atol=1e-5))
            sec = sec+1
    if verbose: print("comparing bolometric ld coeffs")
    ld_coeffs1 =[phb1.getpar('phoebe_ld_xbol1', x), phb1.getpar('phoebe_ld_ybol1', x), phb1.getpar('phoebe_ld_xbol2', x), phb1.getpar('phoebe_ld_ybol2',x)]
    ldx1, ldy1 = b.filter(qualifier='ld_coeffs_bol', component='cow').get_value()
    ldx2, ldy2 = b.filter(qualifier='ld_coeffs_bol', component='pig').get_value()
    ld_coeffs2 = [ldx1, ldy1, ldx2, ldy2]
    assert(np.all(ld_coeffs1==ld_coeffs2))
#            assert(np.all(vels2[x] == rv2))

#        if np.any((vels1[x]-rv2) != 0):
#            print("lightcurve "+str(lcs[x])+" failed")
#        else:
#            print("lightcurve "+str(lcs[x])+" passed")

    return

if __name__ == '__main__':

#    logger= phb2.logger()
    detached = 'default.phoebe'
    weighted = 'weight.phoebe'
    contact = 'contact.phoebe'
#    print "checking detached system"
    legacy_test(weighted, verbose=True)
    legacy_test(detached, verbose=True)
#    print "checking contact system"
    legacy_test(contact, verbose=True)
