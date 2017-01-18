# -----------------------------------------------------------------------------


def parameters():
    from sf.mmck.parameters import p, String
    
    # Define your parameters below by adding to the
    # `p` object.
    #
    # You can define String or Integer parameters.
    #
    # Example:
    #
    #   p.name = String(label='Project Name')
    #   p.voices = Integer(5, range=(3, 17), step=2)
    #   p.spread = Integer(5, range=(0, 128))
    
    p.name = String('My FM Synth', label='Project Name')
    p.algorithm = String('4- 43 3. 2. 1.', label='Algorithm')
    

# -----------------------------------------------------------------------------


def project():
    from sf.mmck.project import c, p, project
    from rv.api import m

    from collections import defaultdict

    # Construct the MetaModule interior by
    # attaching modules to the `project` object.
    # Consult the `rv` documentation for details.
    # http://radiant-voices.rtfd.io/
    #
    # Expose controllers you'd like to manipulate
    # by adding them to the `c` object, using
    # `(module, ctl_name)` notation.
    #
    # Group them together using `Group` objects.
    #
    # Example:
    #
    #   gen = project.new_module(
    #       m.AnalogGenerator,
    #       polyphony_ch=1,
    #       sustain=False,
    #   )
    #   gen >> project.output
    #   c.attack = (gen, 'attack')
    #   c.release = (gen, 'release')


    def sin_generator(group, name):
        module = project.new_module(
            m.AnalogGenerator,
            name=name,
            polyphony_ch=1,
        )
        group.waveform = (module, 'waveform')
        group.sustain = (module, 'sustain')
        group.attack = (module, 'attack')
        group.release = (module, 'release')
        group.duty_cycle = (module, 'duty_cycle')
        return module

    def operator(group, name):
        return sin_generator(group, name)

    operator_factories = None

    # =========================

    project.name = p.name

    note_in = project.new_module(m.MultiSynth, name='note in')

    out_amp = project.new_module(m.Amplifier)
    out_amp >> project.output
    c.master_volume = (out_amp, 'volume')

    forward_graph = defaultdict(list)
    edges = [(src, dest) for src, dest in p.algorithm.split(' ')]
    for src, dest in edges:
        dest = src if dest == '-' else dest
        node = forward_graph[src]
        if dest not in node:
            forward_graph[src].append(dest)

    reverse_graph = defaultdict(list)
    edges = [(src, dest) for src, dest in p.algorithm.split(' ')]
    for src, dest in edges:
        dest = src if dest == '-' else dest
        node = reverse_graph[dest]
        if src not in node:
            reverse_graph[dest].append(src)

    operator_count = len(forward_graph)

    operator_names = set(forward_graph).union(set(reverse_graph))
    operator_names = list(sorted(operator_names))
    operator_names.remove('.')

    operator_factories = operator_factories or ([operator] * operator_count)

    for name in operator_names:
        c['operator_{}'.format(name)] = Group()

    operators = {}
    operator_c_amps = {}
    operator_m_amps = {}
    operator_mods = {}
    operator_multis = {}
    for name, factory in zip(operator_names, operator_factories):
        group = c['operator_{}'.format(name)]
        multi = m.MultiSynth(name='{} note'.format(name))
        oper = factory(group, name='{} oper'.format(name))
        c_amp = m.Amplifier(name='{} c amp'.format(name))
        m_amp = m.Amplifier(name='{} m amp'.format(name))
        mod = m.Modulator(
            modulation_type='phase',
            name='{} mod'.format(name),
        )
        project += [multi, oper, c_amp, m_amp, mod]
        multi >> oper >> c_amp >> mod
        m_amp >> mod
        operators[name] = oper
        operator_c_amps[name] = c_amp
        operator_m_amps[name] = m_amp
        operator_mods[name] = mod
        operator_multis[name] = multi
        group.carrier_amp = (c_amp, 'volume')
        group.modulator_amp = (m_amp, 'volume')

    feedback_ctls = {}
    for dest_key, src_keys in reverse_graph.items():
        if dest_key == '.':
            dest_amp = out_amp
        else:
            dest_amp = operator_m_amps[dest_key]
        for src_key in src_keys:
            src_mod = operator_mods[src_key]
            if src_key == dest_key:
                fb1 = project.new_module(m.Feedback, volume=0)
                fb2 = project.new_module(m.Feedback, volume=0)
                fb_ctl = project.new_module(
                    m.MultiCtl,
                    value=0,
                    name='{} fb'.format(src_key),
                    mappings=[
                        (0, 32768, fb1.controllers['volume'].number),
                        (0, 32768, fb2.controllers['volume'].number),
                    ]
                )
                src_m_amp = operator_m_amps[src_key]
                src_mod >> fb1 >> fb2 >> src_m_amp
                fb_ctl >> [fb1, fb2]
                feedback_ctls[src_key] = fb_ctl
                group = c['operator_{}'.format(src_key)]
                group.feedback = (fb_ctl, 'value')
            else:
                src_mod >> dest_amp

    note_in >> list(operator_multis.values())
