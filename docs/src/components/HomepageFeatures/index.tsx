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
    title: '12+ Simulation Methods',
    emoji: '🧠',
    description: (
      <>
        Implements patient simulation methods from top venues including ACL,
        EMNLP, CHI, and CIKM. Each method is validated for research quality.
      </>
    ),
  },
  {
    title: 'Easy to Use',
    emoji: '⚡',
    description: (
      <>
        Simple CLI interface and Python API. Run simulations with a single
        command: <code>python -m examples.simulate client=patientPsi</code>
      </>
    ),
  },
  {
    title: 'Research Ready',
    emoji: '📊',
    description: (
      <>
        Built-in evaluation tools for measuring simulation quality, therapist
        performance, and research reproducibility. Export results in multiple formats.
      </>
    ),
  },
  {
    title: 'Highly Extensible',
    emoji: '🔧',
    description: (
      <>
        Add new patient agents, therapist types, and evaluators with a clean
        plugin architecture. Full documentation for contributors.
      </>
    ),
  },
  {
    title: 'Multi-Modal Support',
    emoji: '🌐',
    description: (
      <>
        CLI, web interface (Chainlit), and programmatic API. Use the interface
        that fits your workflow - from quick experiments to full integrations.
      </>
    ),
  },
  {
    title: 'LangChain Powered',
    emoji: '🔗',
    description: (
      <>
        Built on LangChain and LangGraph for robust LLM interactions. Supports
        multiple model providers including OpenAI, Anthropic, and local models.
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
