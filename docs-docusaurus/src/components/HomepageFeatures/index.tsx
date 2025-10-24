import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: '多主体模拟',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        支持狩猎采集者、普通农民和水稻农民三类人群的互动模拟，
        考虑地形因素对人群分布的影响。
      </>
    ),
  },
  {
    title: '灵活配置',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        提供灵活的转化机制控制，可独立开关不同类型的转化，
        支持人口增长、迁移和转化等动态过程。
      </>
    ),
  },
  {
    title: '数据可视化',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        提供多种数据可视化方法，如人口分布热力图、人口变化趋势图等，
        严格的人口守恒机制确保扩散和合并过程的准确性。
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
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
