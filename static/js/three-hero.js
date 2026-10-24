/**
 * Homepage hero: a stylised miniature German town in Three.js.
 *
 * Everything is built from primitive geometry -- no model downloads, no
 * textures -- so the scene costs one module import and renders in a few
 * hundred triangles. Vocabulary words float above the town; clicking one
 * raises an information card supplied by Django via a data attribute.
 *
 * The module is imported dynamically and only when the page asks for it,
 * the device supports WebGL, and the learner has not opted out of motion.
 */

import * as THREE from '../vendor/three.module.min.js';
import { isCompactDevice, prefersReducedMotion } from './utils.js';

const PALETTE = {
  ground:   0xEDE5D7,
  road:     0xD8CFC0,
  wallA:    0xF6F1E8,
  wallB:    0xE9DECD,
  wallC:    0xDCCFBA,
  roofRed:  0xC0261A,
  roofDark: 0x4A4741,
  roofTile: 0xB5533F,
  trim:     0x77726A,
  foliage:  0x2A6F52,
  foliage2: 0x46946F,
  trunk:    0x6B5443,
  glass:    0xC4D7E4,
  gold:     0xF5B821,
  train:    0x8A8F98,
  car:      0x2F5D8C,
  car2:     0xB98600,
  water:    0xBCD3E4,
  stone:    0xEFE7D8,
};

function material(color, options = {}) {
  return new THREE.MeshLambertMaterial({ color, ...options });
}

/** A simple house: box body plus a prism roof. */
function makeHouse({ width = 1, depth = 1, height = 1.4, wall, roof, roofHeight = 0.5 }) {
  const group = new THREE.Group();

  const body = new THREE.Mesh(
    new THREE.BoxGeometry(width, height, depth),
    material(wall)
  );
  body.position.y = height / 2;
  body.castShadow = true;
  body.receiveShadow = true;
  group.add(body);

  // A 4-sided cone makes a clean gabled roof at almost no cost.
  const roofMesh = new THREE.Mesh(
    new THREE.ConeGeometry(Math.max(width, depth) * 0.79, roofHeight, 4),
    material(roof)
  );
  roofMesh.position.y = height + roofHeight / 2;
  roofMesh.rotation.y = Math.PI / 4;
  roofMesh.castShadow = true;
  group.add(roofMesh);

  // Two window strips to read as a building rather than a block.
  const windows = new THREE.Mesh(
    new THREE.BoxGeometry(width * 0.62, height * 0.18, depth + 0.02),
    material(PALETTE.glass)
  );
  windows.position.y = height * 0.62;
  group.add(windows);

  return group;
}

function makeTree(scale = 1) {
  const group = new THREE.Group();
  const trunk = new THREE.Mesh(
    new THREE.CylinderGeometry(0.06, 0.08, 0.45, 6),
    material(PALETTE.trunk)
  );
  trunk.position.y = 0.22;
  group.add(trunk);

  const crown = new THREE.Mesh(
    new THREE.IcosahedronGeometry(0.34, 0),
    material(Math.random() > 0.5 ? PALETTE.foliage : PALETTE.foliage2, { flatShading: true })
  );
  crown.position.y = 0.66;
  crown.castShadow = true;
  group.add(crown);

  group.scale.setScalar(scale);
  return group;
}

function makeCafe() {
  const group = new THREE.Group();
  group.add(makeHouse({
    width: 1.5, depth: 1.2, height: 1.0, roofHeight: 0.34,
    wall: PALETTE.wallA, roof: PALETTE.roofRed,
  }));

  // Awning: a thin, tilted slab in café stripes.
  const awning = new THREE.Mesh(
    new THREE.BoxGeometry(1.55, 0.06, 0.55),
    material(PALETTE.roofRed)
  );
  awning.position.set(0, 0.78, 0.78);
  awning.rotation.x = -0.22;
  group.add(awning);

  // Two pavement tables.
  for (const x of [-0.45, 0.45]) {
    const top = new THREE.Mesh(
      new THREE.CylinderGeometry(0.16, 0.16, 0.04, 10),
      material(PALETTE.wallB)
    );
    top.position.set(x, 0.32, 1.2);
    group.add(top);
    const leg = new THREE.Mesh(
      new THREE.CylinderGeometry(0.03, 0.03, 0.3, 6),
      material(PALETTE.trim)
    );
    leg.position.set(x, 0.15, 1.2);
    group.add(leg);
  }

  return group;
}

function makeStation() {
  const group = new THREE.Group();

  const hall = makeHouse({
    width: 2.4, depth: 1.3, height: 1.15, roofHeight: 0.42,
    wall: PALETTE.wallC, roof: PALETTE.roofDark,
  });
  group.add(hall);

  // Clock tower -- the visual anchor of a German Bahnhof.
  const tower = new THREE.Mesh(
    new THREE.BoxGeometry(0.55, 2.0, 0.55),
    material(PALETTE.wallB)
  );
  tower.position.set(-1.35, 1.0, 0);
  tower.castShadow = true;
  group.add(tower);

  const spire = new THREE.Mesh(
    new THREE.ConeGeometry(0.44, 0.6, 4),
    material(PALETTE.roofDark)
  );
  spire.position.set(-1.35, 2.3, 0);
  spire.rotation.y = Math.PI / 4;
  group.add(spire);

  const clock = new THREE.Mesh(
    new THREE.CircleGeometry(0.17, 16),
    material(PALETTE.gold)
  );
  clock.position.set(-1.35, 1.72, 0.29);
  group.add(clock);

  // Platform and a stub train.
  const platform = new THREE.Mesh(
    new THREE.BoxGeometry(3.4, 0.12, 0.7),
    material(PALETTE.road)
  );
  platform.position.set(0.2, 0.06, -1.15);
  platform.receiveShadow = true;
  group.add(platform);

  const train = new THREE.Group();
  const body = new THREE.Mesh(
    new THREE.BoxGeometry(2.2, 0.5, 0.42),
    material(PALETTE.train)
  );
  body.position.y = 0.3;
  train.add(body);
  const stripe = new THREE.Mesh(
    new THREE.BoxGeometry(2.22, 0.09, 0.44),
    material(PALETTE.roofRed)
  );
  stripe.position.y = 0.42;
  train.add(stripe);
  train.position.set(0.2, 0.12, -1.85);
  train.userData.drift = true;
  group.add(train);
  group.userData.train = train;

  return group;
}

function makeSign(text = '') {
  const group = new THREE.Group();
  const post = new THREE.Mesh(
    new THREE.CylinderGeometry(0.025, 0.025, 0.7, 6),
    material(PALETTE.trim)
  );
  post.position.y = 0.35;
  group.add(post);

  const plate = new THREE.Mesh(
    new THREE.BoxGeometry(0.52, 0.16, 0.03),
    material(0xF6F1E8)
  );
  plate.position.y = 0.72;
  group.add(plate);
  group.userData.label = text;
  return group;
}

function makeCar(color) {
  const group = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.15, 0.22), material(color));
  body.position.y = 0.11;
  group.add(body);
  const cabin = new THREE.Mesh(
    new THREE.BoxGeometry(0.22, 0.12, 0.2),
    material(PALETTE.glass)
  );
  cabin.position.set(-0.02, 0.23, 0);
  group.add(cabin);
  return group;
}

/** A subtle nod to the flag: three slim bars on a pole, not a waving banner. */
function makeFlagPole() {
  const group = new THREE.Group();
  const pole = new THREE.Mesh(
    new THREE.CylinderGeometry(0.018, 0.018, 1.5, 6),
    material(PALETTE.trim)
  );
  pole.position.y = 0.75;
  group.add(pole);

  const colors = [0x1C1B19, 0x9B2226, 0xC99700];
  colors.forEach((color, index) => {
    const bar = new THREE.Mesh(
      new THREE.BoxGeometry(0.34, 0.075, 0.012),
      material(color)
    );
    bar.position.set(0.19, 1.34 - index * 0.078, 0);
    group.add(bar);
  });
  return group;
}

/** The Brandenburg Gate, reduced to its silhouette: columns and a quadriga. */
function makeGate() {
  const group = new THREE.Group();
  const stone = material(0xEFE7D8);

  const base = new THREE.Mesh(new THREE.BoxGeometry(2.5, 0.12, 0.9), stone);
  base.position.y = 0.06;
  base.receiveShadow = true;
  group.add(base);

  // Six columns, which is what makes it read as the Brandenburger Tor.
  for (let i = 0; i < 6; i += 1) {
    const column = new THREE.Mesh(
      new THREE.CylinderGeometry(0.1, 0.11, 1.3, 8),
      stone
    );
    column.position.set(-1.0 + i * 0.4, 0.71, 0);
    column.castShadow = true;
    group.add(column);
  }

  const architrave = new THREE.Mesh(new THREE.BoxGeometry(2.5, 0.3, 0.95), stone);
  architrave.position.y = 1.51;
  architrave.castShadow = true;
  group.add(architrave);

  // The quadriga, suggested rather than modelled.
  const chariot = new THREE.Mesh(
    new THREE.BoxGeometry(0.55, 0.22, 0.3),
    material(0x8C7A5B)
  );
  chariot.position.y = 1.77;
  group.add(chariot);
  for (let i = 0; i < 4; i += 1) {
    const horse = new THREE.Mesh(
      new THREE.BoxGeometry(0.1, 0.2, 0.26),
      material(0x8C7A5B)
    );
    horse.position.set(-0.18 + i * 0.12, 1.86, 0);
    group.add(horse);
  }

  return group;
}

/** A church: nave, steep roof and the tall spire that anchors the skyline. */
function makeChurch() {
  const group = new THREE.Group();

  const nave = new THREE.Mesh(
    new THREE.BoxGeometry(1.1, 1.2, 1.9),
    material(PALETTE.wallA)
  );
  nave.position.y = 0.6;
  nave.castShadow = true;
  group.add(nave);

  const roof = new THREE.Mesh(
    new THREE.CylinderGeometry(0.01, 0.78, 0.6, 3),
    material(PALETTE.roofDark)
  );
  roof.position.y = 1.5;
  roof.rotation.y = Math.PI / 2;
  roof.scale.z = 2.4;
  roof.castShadow = true;
  group.add(roof);

  const tower = new THREE.Mesh(
    new THREE.BoxGeometry(0.62, 2.6, 0.62),
    material(PALETTE.wallB)
  );
  tower.position.set(0, 1.3, -1.25);
  tower.castShadow = true;
  group.add(tower);

  const spire = new THREE.Mesh(
    new THREE.ConeGeometry(0.5, 1.5, 4),
    material(PALETTE.roofDark)
  );
  spire.position.set(0, 3.35, -1.25);
  spire.rotation.y = Math.PI / 4;
  spire.castShadow = true;
  group.add(spire);

  const clockFace = new THREE.Mesh(
    new THREE.CircleGeometry(0.16, 16),
    material(PALETTE.gold)
  );
  clockFace.position.set(0, 2.2, -0.93);
  group.add(clockFace);

  const cross = new THREE.Mesh(
    new THREE.BoxGeometry(0.04, 0.3, 0.04),
    material(PALETTE.gold)
  );
  cross.position.set(0, 4.25, -1.25);
  group.add(cross);

  return group;
}

/** A market stall with a striped awning. */
function makeStall(colour) {
  const group = new THREE.Group();

  const table = new THREE.Mesh(
    new THREE.BoxGeometry(0.7, 0.06, 0.45),
    material(0xC9B99C)
  );
  table.position.y = 0.38;
  group.add(table);

  for (const [x, z] of [[-0.3, -0.18], [0.3, -0.18], [-0.3, 0.18], [0.3, 0.18]]) {
    const leg = new THREE.Mesh(
      new THREE.CylinderGeometry(0.022, 0.022, 0.38, 5),
      material(PALETTE.trim)
    );
    leg.position.set(x, 0.19, z);
    group.add(leg);
  }

  const awning = new THREE.Mesh(
    new THREE.CylinderGeometry(0.44, 0.44, 0.75, 8, 1, false, 0, Math.PI),
    material(colour)
  );
  awning.rotation.z = Math.PI / 2;
  awning.rotation.y = Math.PI / 2;
  awning.position.y = 0.74;
  group.add(awning);

  // Produce on the table, as three small spheres.
  for (let i = 0; i < 3; i += 1) {
    const crate = new THREE.Mesh(
      new THREE.SphereGeometry(0.07, 8, 6),
      material(i % 2 ? 0xC0261A : 0xB98600)
    );
    crate.position.set(-0.2 + i * 0.2, 0.47, 0);
    group.add(crate);
  }

  return group;
}

/** A tram, which is more German than a car and reads instantly at this scale. */
function makeTram() {
  const group = new THREE.Group();

  const body = new THREE.Mesh(
    new THREE.BoxGeometry(1.5, 0.42, 0.34),
    material(0xF2C230)
  );
  body.position.y = 0.3;
  body.castShadow = true;
  group.add(body);

  const windows = new THREE.Mesh(
    new THREE.BoxGeometry(1.3, 0.16, 0.36),
    material(PALETTE.glass)
  );
  windows.position.y = 0.36;
  group.add(windows);

  const skirt = new THREE.Mesh(
    new THREE.BoxGeometry(1.5, 0.1, 0.36),
    material(0x5A5750)
  );
  skirt.position.y = 0.1;
  group.add(skirt);

  const pole = new THREE.Mesh(
    new THREE.CylinderGeometry(0.014, 0.014, 0.4, 5),
    material(PALETTE.trim)
  );
  pole.position.set(-0.4, 0.68, 0);
  pole.rotation.z = -0.3;
  group.add(pole);

  return group;
}

/** A street lamp. */
function makeLamp() {
  const group = new THREE.Group();
  const post = new THREE.Mesh(
    new THREE.CylinderGeometry(0.022, 0.03, 0.8, 6),
    material(PALETTE.trim)
  );
  post.position.y = 0.4;
  group.add(post);

  const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.07, 8, 6),
    new THREE.MeshLambertMaterial({ color: 0xFFF1C9, emissive: 0xFFE08A, emissiveIntensity: 0.6 })
  );
  head.position.y = 0.85;
  group.add(head);
  return group;
}

/** A low-poly cloud: three overlapping spheres. */
function makeCloud() {
  const group = new THREE.Group();
  const cloudMaterial = new THREE.MeshLambertMaterial({
    color: 0xFFFFFF, transparent: true, opacity: 0.9,
  });
  [[0, 0, 0, 0.42], [0.36, -0.06, 0.05, 0.3], [-0.34, -0.08, -0.04, 0.27]].forEach(
    ([x, y, z, r]) => {
      const puff = new THREE.Mesh(new THREE.SphereGeometry(r, 8, 6), cloudMaterial);
      puff.position.set(x, y, z);
      group.add(puff);
    }
  );
  return group;
}

/** A bird: two angled planes that flap. */
function makeBird() {
  const group = new THREE.Group();
  const wingMaterial = new THREE.MeshBasicMaterial({
    color: 0x5A5750, side: THREE.DoubleSide,
  });
  const left = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.05), wingMaterial);
  const right = new THREE.Mesh(new THREE.PlaneGeometry(0.16, 0.05), wingMaterial);
  left.position.x = -0.08;
  right.position.x = 0.08;
  group.add(left, right);
  group.userData.wings = [left, right];
  return group;
}

/** Renders a word onto a canvas sprite -- cheap, crisp and always camera-facing. */
function makeWordSprite(word, scale) {
  const canvas = document.createElement('canvas');
  const pixelRatio = Math.min(window.devicePixelRatio || 1, 2);
  const fontSize = 52;
  const padding = 26;

  const context = canvas.getContext('2d');
  context.font = `600 ${fontSize}px "Fraunces", Georgia, serif`;
  const width = Math.ceil(context.measureText(word).width) + padding * 2;
  const height = fontSize + padding * 1.5;

  canvas.width = width * pixelRatio;
  canvas.height = height * pixelRatio;
  context.scale(pixelRatio, pixelRatio);

  const radius = height / 2;
  context.fillStyle = 'rgba(255,255,255,0.94)';
  context.strokeStyle = 'rgba(28,27,25,0.10)';
  context.lineWidth = 1.5;
  context.beginPath();
  if (typeof context.roundRect === 'function') {
    context.roundRect(1, 1, width - 2, height - 2, radius);
  } else {
    // Safari < 16 has no roundRect; a plain rect still reads fine.
    context.rect(1, 1, width - 2, height - 2);
  }
  context.fill();
  context.stroke();

  context.fillStyle = '#1C1B19';
  context.font = `600 ${fontSize}px "Fraunces", Georgia, serif`;
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.fillText(word, width / 2, height / 2 + 2);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;

  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false })
  );
  const spriteScale = scale * (width / height);
  sprite.scale.set(spriteScale, scale, 1);
  sprite.renderOrder = 10;
  return sprite;
}

class HeroScene {
  constructor(container, words) {
    this.container = container;
    this.words = words;
    this.compact = isCompactDevice();
    this.clock = new THREE.Clock();
    this.pointer = new THREE.Vector2(-2, -2);
    this.raycaster = new THREE.Raycaster();
    this.wordSprites = [];
    this.active = null;
    this.running = false;
    this.targetRotation = 0;
    this.currentRotation = 0;

    this.card = container.querySelector('[data-scene-card]');
    this.loader = container.querySelector('[data-scene-loader]');

    this.build();
    this.bind();
    this.start();
  }

  build() {
    const { clientWidth: width, clientHeight: height } = this.container;

    this.renderer = new THREE.WebGLRenderer({
      antialias: !this.compact,
      alpha: true,
      powerPreference: 'low-power',
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, this.compact ? 1.5 : 2));
    this.renderer.setSize(width, height);
    this.renderer.shadowMap.enabled = !this.compact;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.container.insertBefore(this.renderer.domElement, this.container.firstChild);

    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.Fog(0xF4EFE7, 12, 26);

    this.camera = new THREE.PerspectiveCamera(38, width / height, 0.1, 100);
    this.camera.position.set(6.4, 5.2, 7.2);
    this.camera.lookAt(0, 0.9, 0);

    this.town = new THREE.Group();
    this.scene.add(this.town);

    this.addLights();
    this.addGround();
    this.addBuildings();
    this.addDetails();
    this.addWords();
  }

  addLights() {
    this.scene.add(new THREE.HemisphereLight(0xFFFBF2, 0xD6CCBC, 1.15));

    const sun = new THREE.DirectionalLight(0xFFF4DF, 1.25);
    sun.position.set(5, 9, 4);
    if (!this.compact) {
      sun.castShadow = true;
      sun.shadow.mapSize.set(1024, 1024);
      sun.shadow.camera.near = 1;
      sun.shadow.camera.far = 30;
      const extent = 9;
      Object.assign(sun.shadow.camera, {
        left: -extent, right: extent, top: extent, bottom: -extent,
      });
      sun.shadow.camera.updateProjectionMatrix();
    }
    this.scene.add(sun);

    const fill = new THREE.DirectionalLight(0xE7EEF6, 0.35);
    fill.position.set(-6, 4, -5);
    this.scene.add(fill);
  }

  addGround() {
    const ground = new THREE.Mesh(
      new THREE.CircleGeometry(8.2, this.compact ? 32 : 64),
      material(PALETTE.ground)
    );
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    this.town.add(ground);

    // A cobbled square and two roads leading off it.
    const square = new THREE.Mesh(
      new THREE.CircleGeometry(2.1, 32),
      material(PALETTE.road)
    );
    square.rotation.x = -Math.PI / 2;
    square.position.y = 0.01;
    this.town.add(square);

    [0, Math.PI / 2].forEach((angle) => {
      const road = new THREE.Mesh(
        new THREE.PlaneGeometry(1.15, 14),
        material(PALETTE.road)
      );
      road.rotation.x = -Math.PI / 2;
      road.rotation.z = angle;
      road.position.y = 0.008;
      this.town.add(road);
    });

    // A river cutting across the south-east, with a bridge over the road.
    const river = new THREE.Mesh(
      new THREE.PlaneGeometry(1.5, 16),
      material(PALETTE.water)
    );
    river.rotation.x = -Math.PI / 2;
    river.rotation.z = -0.75;
    river.position.set(1.4, 0.012, 2.4);
    this.town.add(river);
    this.river = river;

    const bridge = new THREE.Mesh(
      new THREE.BoxGeometry(2.1, 0.1, 0.8),
      material(PALETTE.stone)
    );
    bridge.position.set(1.4, 0.1, 2.4);
    bridge.rotation.y = 0.82;
    bridge.castShadow = true;
    this.town.add(bridge);

    for (const offset of [-0.6, 0.6]) {
      const rail = new THREE.Mesh(
        new THREE.BoxGeometry(2.1, 0.12, 0.05),
        material(PALETTE.trim)
      );
      rail.position.set(1.4 + Math.sin(0.82) * offset, 0.21, 2.4 + Math.cos(0.82) * offset);
      rail.rotation.y = 0.82;
      this.town.add(rail);
    }

    // Tram rails through the square.
    for (const offset of [-0.16, 0.16]) {
      const rail = new THREE.Mesh(
        new THREE.BoxGeometry(12, 0.02, 0.05),
        material(0x9A9287)
      );
      rail.position.set(0, 0.02, 1.0 + offset);
      this.town.add(rail);
    }
  }

  addBuildings() {
    const houses = [
      { x: -3.0, z: -2.4, w: 1.1, d: 1.1, h: 1.6, wall: PALETTE.wallA, roof: PALETTE.roofTile, r: 0.5 },
      { x: -1.7, z: -3.1, w: 1.0, d: 1.0, h: 2.1, wall: PALETTE.wallB, roof: PALETTE.roofRed, r: 0.46 },
      { x:  1.9, z: -2.9, w: 1.2, d: 1.0, h: 1.35, wall: PALETTE.wallC, roof: PALETTE.roofDark, r: 0.5 },
      { x:  3.1, z: -1.5, w: 1.0, d: 1.2, h: 1.8, wall: PALETTE.wallA, roof: PALETTE.roofTile, r: 0.46 },
      { x: -3.2, z:  1.6, w: 1.2, d: 1.1, h: 1.45, wall: PALETTE.wallB, roof: PALETTE.roofRed, r: 0.5 },
      { x:  3.2, z:  2.1, w: 1.1, d: 1.1, h: 1.7, wall: PALETTE.wallC, roof: PALETTE.roofTile, r: 0.48 },
      { x:  1.4, z:  3.3, w: 1.0, d: 1.0, h: 1.3, wall: PALETTE.wallA, roof: PALETTE.roofDark, r: 0.44 },
    ];

    houses.forEach((spec) => {
      const house = makeHouse({
        width: spec.w, depth: spec.d, height: spec.h,
        wall: spec.wall, roof: spec.roof, roofHeight: spec.r,
      });
      house.position.set(spec.x, 0, spec.z);
      house.rotation.y = (Math.random() - 0.5) * 0.3;
      this.town.add(house);
    });

    const cafe = makeCafe();
    cafe.position.set(-1.6, 0, 1.9);
    cafe.rotation.y = 0.25;
    this.town.add(cafe);

    const station = makeStation();
    station.position.set(0.2, 0, -4.4);
    this.town.add(station);
    this.train = station.userData.train;

    const gate = makeGate();
    gate.position.set(-3.9, 0, -0.6);
    gate.rotation.y = Math.PI / 2;
    this.town.add(gate);

    const church = makeChurch();
    church.position.set(2.7, 0, -3.4);
    church.rotation.y = -0.35;
    this.town.add(church);
  }

  addDetails() {
    const treeSpots = [
      [-4.2, 0.2], [-2.4, 3.6], [2.6, -4.4], [4.3, 0.6],
      [-0.8, 4.2], [4.1, 3.3], [-4.4, -0.9], [0.9, -1.6],
    ];
    const trees = this.compact ? treeSpots.slice(0, 5) : treeSpots;
    trees.forEach(([x, z]) => {
      const tree = makeTree(0.9 + Math.random() * 0.5);
      tree.position.set(x, 0, z);
      this.town.add(tree);
    });

    [[-1.1, -0.9, 'Bahnhof'], [1.4, 1.1, 'Café'], [-0.4, 2.6, 'Markt']].forEach(
      ([x, z, label]) => {
        const sign = makeSign(label);
        sign.position.set(x, 0, z);
        sign.rotation.y = Math.random() * Math.PI;
        this.town.add(sign);
      }
    );

    const flag = makeFlagPole();
    flag.position.set(2.2, 0, 0.4);
    this.town.add(flag);

    // A market on the square.
    const stallColours = [0xC0261A, 0xF5B821, 0x2A6F52];
    stallColours.slice(0, this.compact ? 2 : 3).forEach((colour, index) => {
      const stall = makeStall(colour);
      const angle = -0.6 + index * 0.55;
      stall.position.set(Math.cos(angle) * 1.5, 0, Math.sin(angle) * 1.5 + 0.4);
      stall.rotation.y = -angle;
      this.town.add(stall);
    });

    if (!this.compact) {
      [[-1.9, 0.75], [1.9, 0.75], [-1.9, -1.1], [1.9, -1.1]].forEach(([x, z]) => {
        const lamp = makeLamp();
        lamp.position.set(x, 0, z);
        this.town.add(lamp);
      });
    }

    // The tram runs along the rails laid in addGround().
    this.tram = makeTram();
    this.tram.position.set(0, 0.04, 1.0);
    this.town.add(this.tram);

    this.cars = [];
    if (!this.compact) {
      [[PALETTE.car, 0], [PALETTE.car2, Math.PI]].forEach(([color, phase], index) => {
        const car = makeCar(color);
        car.userData.phase = phase;
        car.userData.axis = index;
        this.town.add(car);
        this.cars.push(car);
      });
    }

    // Clouds and birds live in the scene, not the town, so they keep drifting
    // while the town turns under the cursor.
    this.clouds = [];
    const cloudCount = this.compact ? 3 : 5;
    for (let i = 0; i < cloudCount; i += 1) {
      const cloud = makeCloud();
      cloud.position.set(
        -7 + Math.random() * 14,
        4.2 + Math.random() * 1.8,
        -5 + Math.random() * 8
      );
      cloud.scale.setScalar(0.8 + Math.random() * 0.7);
      cloud.userData.speed = 0.12 + Math.random() * 0.18;
      this.scene.add(cloud);
      this.clouds.push(cloud);
    }

    this.birds = [];
    if (!this.compact) {
      for (let i = 0; i < 4; i += 1) {
        const bird = makeBird();
        bird.userData.radius = 4.5 + i * 0.5;
        bird.userData.height = 3.6 + (i % 2) * 0.5;
        bird.userData.phase = i * 1.7;
        bird.userData.speed = 0.22 + i * 0.03;
        this.scene.add(bird);
        this.birds.push(bird);
      }
    }
  }

  addWords() {
    // Alternating rings and four distinct heights keep the labels from
    // stacking on top of each other in screen space as they orbit.
    const rings = [3.1, 4.6];
    const count = this.words.length;

    this.words.forEach((entry, index) => {
      const sprite = makeWordSprite(entry.word, 0.42);
      // Golden-angle spacing scatters them far better than an even divide.
      const angle = index * 2.399963 + (index % 2) * 0.6;
      const radius = rings[index % rings.length];
      const height = 2.15 + (index % 4) * 0.72;
      sprite.position.set(
        Math.cos(angle) * radius,
        height,
        Math.sin(angle) * radius
      );
      void count;
      sprite.userData = {
        ...entry,
        baseY: height,
        phase: index * 0.9,
        angle,
        radius,
        baseWidth: sprite.scale.x,
        baseHeight: sprite.scale.y,
        scaleFactor: 1,
        opacity: 1,
      };
      this.wordSprites.push(sprite);
      this.scene.add(sprite);
    });
  }

  bind() {
    const canvas = this.renderer.domElement;
    canvas.style.cursor = 'grab';

    this.onPointerMove = (event) => {
      const rect = canvas.getBoundingClientRect();
      this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      // Gentle look-around: the town leans towards the cursor.
      this.targetRotation = this.pointer.x * 0.42;
    };

    this.onPointerLeave = () => {
      this.pointer.set(-2, -2);
      this.targetRotation = 0;
      canvas.style.cursor = 'grab';
    };

    this.onClick = (event) => {
      const rect = canvas.getBoundingClientRect();
      this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      this.raycaster.setFromCamera(this.pointer, this.camera);
      const hit = this.raycaster.intersectObjects(this.wordSprites, false)[0];
      if (hit) this.select(hit.object);
      else this.closeCard();
    };

    canvas.addEventListener('pointermove', this.onPointerMove);
    canvas.addEventListener('pointerleave', this.onPointerLeave);
    canvas.addEventListener('click', this.onClick);

    this.onResize = () => {
      const { clientWidth: width, clientHeight: height } = this.container;
      if (!width || !height) return;
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(width, height);
      this.containerRect = this.container.getBoundingClientRect();
    };
    window.addEventListener('resize', this.onResize);

    // Pause the render loop whenever the scene is off-screen or the tab hides.
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) this.start();
        else this.stop();
      });
    }, { threshold: 0.01 });
    this.observer.observe(this.container);

    this.onVisibility = () => {
      if (document.hidden) this.stop();
      else this.start();
    };
    document.addEventListener('visibilitychange', this.onVisibility);

    if (this.card) {
      this.card.addEventListener('click', (event) => {
        if (event.target.closest('[data-scene-card-close]')) this.closeCard();
      });
    }
  }

  select(sprite) {
    this.active = sprite;
    sprite.material.opacity = 1;
    this.renderCard(sprite.userData);
  }

  /** Fill the card with a word's detail. Called once per selection. */
  renderCard(data) {
    if (!this.card) return;
    const set = (selector, value) => {
      const node = this.card.querySelector(selector);
      if (node) node.textContent = value || '';
    };

    set('[data-card-word]', data.display || data.word);
    set('[data-card-translation]', data.translation);
    set('[data-card-example]', data.example);
    set('[data-card-example-en]', data.exampleEn);

    const example = this.card.querySelector('[data-card-example-wrap]');
    if (example) example.hidden = !data.example;

    this.card.classList.add('is-visible');
    // The container box only changes on resize, so measure it once here
    // rather than on every animation frame.
    this.containerRect = this.container.getBoundingClientRect();
    this.cardSize = {
      width: this.card.offsetWidth,
      height: this.card.offsetHeight,
    };
    this.positionCard();
  }

  /** Keep the card over its sprite as the town rotates. Cheap enough per frame. */
  positionCard() {
    if (!this.card || !this.active || !this.containerRect) return;

    const projected = this.active.position.clone().project(this.camera);
    const { width, height } = this.containerRect;
    const x = (projected.x * 0.5 + 0.5) * width;
    const y = (-projected.y * 0.5 + 0.5) * height;

    const card = this.cardSize;
    const left = Math.max(12, Math.min(x - card.width / 2, width - card.width - 12));
    const top = Math.max(12, Math.min(y + 18, height - card.height - 12));
    this.card.style.transform = `translate(${Math.round(left)}px, ${Math.round(top)}px)`;
  }

  closeCard() {
    this.active = null;
    if (this.card) this.card.classList.remove('is-visible');
  }

  animate = () => {
    if (!this.running) return;
    this.frame = requestAnimationFrame(this.animate);

    const elapsed = this.clock.getElapsedTime();

    // Ease the town towards the pointer-driven rotation.
    this.currentRotation += (this.targetRotation - this.currentRotation) * 0.055;
    this.town.rotation.y = this.currentRotation + elapsed * 0.035;

    this.wordSprites.forEach((sprite) => {
      const data = sprite.userData;
      sprite.position.y = data.baseY + Math.sin(elapsed * 0.72 + data.phase) * 0.16;
      const angle = data.angle + elapsed * 0.045;
      sprite.position.x = Math.cos(angle) * data.radius;
      sprite.position.z = Math.sin(angle) * data.radius;

      // Words orbiting behind the town recede instead of fighting the ones
      // in front. One distance check per sprite -- negligible.
      const distance = sprite.position.distanceTo(this.camera.position);
      const wanted = THREE.MathUtils.clamp(
        THREE.MathUtils.mapLinear(distance, 8.5, 13.5, 1, 0.28), 0.28, 1
      );
      data.opacity += (wanted - data.opacity) * 0.1;
      if (this.active !== sprite) {
        sprite.material.opacity = this.active ? data.opacity * 0.45 : data.opacity;
      }
    });

    if (this.train) {
      this.train.position.x = 0.2 + Math.sin(elapsed * 0.28) * 1.6;
    }

    if (this.tram) {
      // Runs the length of the rails, pauses at the square, then returns.
      const sweep = Math.sin(elapsed * 0.22);
      this.tram.position.x = sweep * 4.6;
      this.tram.rotation.y = Math.cos(elapsed * 0.22) > 0 ? 0 : Math.PI;
    }

    this.clouds?.forEach((cloud) => {
      cloud.position.x += cloud.userData.speed * 0.016;
      if (cloud.position.x > 8) cloud.position.x = -8;
    });

    this.birds?.forEach((bird) => {
      const angle = elapsed * bird.userData.speed + bird.userData.phase;
      bird.position.set(
        Math.cos(angle) * bird.userData.radius,
        bird.userData.height + Math.sin(angle * 2) * 0.25,
        Math.sin(angle) * bird.userData.radius
      );
      bird.rotation.y = -angle;
      const flap = Math.sin(elapsed * 9 + bird.userData.phase) * 0.7;
      bird.userData.wings[0].rotation.z = flap;
      bird.userData.wings[1].rotation.z = -flap;
    });

    this.cars?.forEach((car) => {
      const t = (elapsed * 0.35 + car.userData.phase) % (Math.PI * 2);
      const travel = Math.sin(t) * 5;
      if (car.userData.axis === 0) {
        car.position.set(travel, 0.02, 0.32);
        car.rotation.y = Math.cos(t) > 0 ? 0 : Math.PI;
      } else {
        car.position.set(-0.32, 0.02, travel);
        car.rotation.y = Math.cos(t) > 0 ? Math.PI / 2 : -Math.PI / 2;
      }
    });

    // Hover feedback on the floating words.
    this.raycaster.setFromCamera(this.pointer, this.camera);
    const hovered = this.raycaster.intersectObjects(this.wordSprites, false)[0];
    this.renderer.domElement.style.cursor = hovered ? 'pointer' : 'grab';
    this.wordSprites.forEach((sprite) => {
      // Ease towards the hover size, preserving the sprite's aspect ratio by
      // tracking a single factor rather than scaling x and y independently.
      const wanted = hovered && hovered.object === sprite ? 1.14 : 1;
      const data = sprite.userData;
      data.scaleFactor += (wanted - data.scaleFactor) * 0.18;
      sprite.scale.set(
        data.baseWidth * data.scaleFactor,
        data.baseHeight * data.scaleFactor,
        1
      );
    });

    if (this.active) this.positionCard();

    this.renderer.render(this.scene, this.camera);
  };

  start() {
    if (this.running) return;
    this.running = true;
    this.frame = requestAnimationFrame(this.animate);
    if (this.loader) this.loader.classList.add('is-hidden');
  }

  stop() {
    this.running = false;
    if (this.frame) cancelAnimationFrame(this.frame);
  }

  dispose() {
    this.stop();
    this.observer?.disconnect();
    window.removeEventListener('resize', this.onResize);
    document.removeEventListener('visibilitychange', this.onVisibility);
    this.scene.traverse((object) => {
      object.geometry?.dispose();
      if (Array.isArray(object.material)) object.material.forEach((m) => m.dispose());
      else object.material?.dispose();
      object.material?.map?.dispose();
    });
    this.renderer.dispose();
    this.renderer.domElement.remove();
  }
}

export function initHeroScene(container) {
  if (prefersReducedMotion()) return null;
  let words = [];
  try {
    words = JSON.parse(container.dataset.words || '[]');
  } catch {
    words = [];
  }
  if (!words.length) return null;

  const fallback = container.querySelector('[data-scene-fallback]');
  if (fallback) fallback.hidden = true;

  return new HeroScene(container, words);
}

export default initHeroScene;
