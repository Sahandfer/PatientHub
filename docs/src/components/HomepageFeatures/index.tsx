import type { ReactNode } from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  emoji: string;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: '15 Client Simulation Methods',
    emoji: '🧠',
    description: (
      <>
        We've reproduced patient simulation methods from publications in top venues including ACL,
        EMNLP, and CHI.
      </>
    ),
  },
  {
    title: 'Fast and Easy to Use',
    emoji: '⚡',
    description: (
      <>
        Simple CLI interface and Python API. Run simulations with a single
        command: <code>python -m examples.simulate client=patientPsi</code>
      </>
    ),
  },

  {
    title: 'Highly Extensible',
    emoji: '🔧',
    description: (
      <>
        Add new agents (Clients, Therapists, etc.) with a clean
        plugin architecture. Full documentation for contributors.
      </>
    ),
  },
];

function Feature({ title, emoji, description }: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <span className={styles.featureEmoji} role="img">{emoji}</span>
      </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
