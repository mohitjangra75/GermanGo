/**
 * A 3D map of Germany, in two modes.
 *
 *   quiz    — markers are unlabelled; the page asks "where is X?" and the
 *             player clicks. Right and wrong answers light up.
 *   teaser  — labelled, slowly turning, used on the homepage as a taste of
 *             the game.
 *
 * The country outline is an extruded THREE.Shape built from about forty
 * coordinates: enough to be recognisably Germany, small enough to ship in
 * this file rather than loading a GeoJSON.
 */

import * as THREE from '../vendor/three.module.min.js';
import { isCompactDevice, prefersReducedMotion } from './utils.js';

/** Normalised outline: x east-positive, y north-positive, roughly -1..1. */
const OUTLINE = [
  [-0.26, 1.00], [-0.05, 0.98], [0.05, 0.88], [0.22, 0.86], [0.30, 0.92],
  [0.42, 0.86], [0.46, 0.70], [0.58, 0.60], [0.62, 0.44], [0.78, 0.36],
  [0.86, 0.20], [0.80, 0.02], [0.86, -0.12], [0.76, -0.26], [0.80, -0.42],
  [0.66, -0.52], [0.54, -0.70], [0.40, -0.76], [0.30, -0.92], [0.12, -1.00],
  [-0.02, -0.92], [-0.12, -0.96], [-0.24, -0.84], [-0.34, -0.86], [-0.42, -0.70],
  [-0.56, -0.62], [-0.62, -0.44], [-0.52, -0.30], [-0.62, -0.16], [-0.58, 0.02],
  [-0.70, 0.14], [-0.66, 0.30], [-0.52, 0.40], [-0.56, 0.56], [-0.42, 0.66],
  [-0.46, 0.80], [-0.34, 0.90],
];

const SCALE = 3.2;

const COLORS = {
  land:      0xF2EADC,
  landSide:  0xDDD2BE,
  water:     0xE4EDF5,
  marker:    0xC0261A,
  active:    0xF5B821,
  correct:   0x2A6F52,
  wrong:     0xC0261A,
};

function buildCountry(compact) {
  const shape = new THREE.Shape();
  OUTLINE.forEach(([x, y], index) => {
    if (index === 0) shape.moveTo(x, y);
    else shape.lineTo(x, y);
  });
  shape.closePath();

  const geometry = new THREE.ExtrudeGeometry(shape, {
    depth: 0.14,
    bevelEnabled: true,
    bevelThickness: 0.022,
    bevelSize: 0.016,
    bevelSegments: compact ? 1 : 2,
    curveSegments: compact ? 2 : 4,
  });
  geometry.rotateX(-Math.PI / 2);
  geometry.scale(SCALE, SCALE, SCALE);

  const mesh = new THREE.Mesh(geometry, [
    new THREE.MeshLambertMaterial({ color: COLORS.land }),
    new THREE.MeshLambertMaterial({ color: COLORS.landSide }),
  ]);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

/** The outline traced as a line, which reads as a border. */
function buildBorder() {
  const points = OUTLINE.map(([x, y]) => new THREE.Vector3(x * SCALE, 0.30, y * SCALE));
  points.push(points[0].clone());
  return new THREE.Line(
    new THREE.BufferGeometry().setFromPoints(points),
    new THREE.LineBasicMaterial({ color: 0xB8AC96, transparent: true, opacity: 0.85 })
  );
}

function buildMarker(color) {
  const group = new THREE.Group();

  const pin = new THREE.Mesh(
    new THREE.ConeGeometry(0.11, 0.36, 12),
    new THREE.MeshLambertMaterial({ color })
  );
  pin.rotation.x = Math.PI;
  pin.position.y = 0.18;
  group.add(pin);

  const head = new THREE.Mesh(
    new THREE.SphereGeometry(0.115, 16, 12),
    new THREE.MeshLambertMaterial({ color })
  );
  head.position.y = 0.4;
  group.add(head);

  const halo = new THREE.Mesh(
    new THREE.RingGeometry(0.17, 0.22, 22),
    new THREE.MeshBasicMaterial({
      color, transparent: true, opacity: 0.45, side: THREE.DoubleSide,
    })
  );
  halo.rotation.x = -Math.PI / 2;
  halo.position.y = 0.02;
  group.add(halo);

  // A generous invisible disc, so a marker is easy to hit on a phone.
  const hit = new THREE.Mesh(
    new THREE.CircleGeometry(0.38, 12),
    new THREE.MeshBasicMaterial({ visible: false })
  );
  hit.rotation.x = -Math.PI / 2;
  hit.position.y = 0.05;
  group.add(hit);

  group.userData.halo = halo;
  group.userData.painted = [pin, head, halo];
  return group;
}

/** A city name drawn to a canvas and shown as a camera-facing sprite. */
function buildLabel(text) {
  const canvas = document.createElement('canvas');
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  const fontSize = 44;
  const padX = 22;
  const padY = 14;

  const context = canvas.getContext('2d');
  context.font = `700 ${fontSize}px Inter, system-ui, sans-serif`;
  const width = Math.ceil(context.measureText(text).width) + padX * 2;
  const height = fontSize + padY * 2;

  canvas.width = width * ratio;
  canvas.height = height * ratio;
  context.scale(ratio, ratio);

  context.fillStyle = 'rgba(255,255,255,0.95)';
  context.strokeStyle = 'rgba(21,22,26,0.10)';
  context.lineWidth = 1.5;
  context.beginPath();
  if (typeof context.roundRect === 'function') {
    context.roundRect(1, 1, width - 2, height - 2, height / 2);
  } else {
    context.rect(1, 1, width - 2, height - 2);
  }
  context.fill();
  context.stroke();

  context.fillStyle = '#15161A';
  context.font = `700 ${fontSize}px Inter, system-ui, sans-serif`;
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.fillText(text, width / 2, height / 2 + 1);

  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = 4;

  const sprite = new THREE.Sprite(
    new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false })
  );
  const scale = 0.3;
  sprite.scale.set(scale * (width / height), scale, 1);
  sprite.renderOrder = 12;
  return sprite;
}

class GermanyMap {
  constructor(container, cities, options = {}) {
    this.container = container;
    this.cities = cities;
    this.mode = options.mode || 'teaser';
    this.compact = isCompactDevice();
    this.clock = new THREE.Clock();
    this.raycaster = new THREE.Raycaster();
    this.pointer = new THREE.Vector2(-2, -2);
    this.markers = [];
    this.locked = false;
    this.running = false;
    this.spin = 0;
    this.targetSpin = 0;

    this.loader = container.querySelector('[data-map-loader]');
    this.build();
    this.bind();
    this.start();
  }

  build() {
    const { clientWidth: width, clientHeight: height } = this.container;

    this.renderer = new THREE.WebGLRenderer({
      antialias: !this.compact, alpha: true, powerPreference: 'low-power',
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, this.compact ? 1.5 : 2));
    this.renderer.setSize(width, height);
    this.renderer.shadowMap.enabled = !this.compact;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.container.insertBefore(this.renderer.domElement, this.container.firstChild);

    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(34, width / height, 0.1, 100);
    this.camera.position.set(0, 9.8, 6.2);
    this.camera.lookAt(0, 0, 0.15);

    this.scene.add(new THREE.HemisphereLight(0xFFFBF2, 0xD6CCBC, 1.15));
    const sun = new THREE.DirectionalLight(0xFFF4DF, 1.05);
    sun.position.set(4, 9, 5);
    if (!this.compact) {
      sun.castShadow = true;
      sun.shadow.mapSize.set(1024, 1024);
      Object.assign(sun.shadow.camera, { left: -8, right: 8, top: 8, bottom: -8 });
      sun.shadow.camera.updateProjectionMatrix();
    }
    this.scene.add(sun);

    this.world = new THREE.Group();
    this.scene.add(this.world);

    const sea = new THREE.Mesh(
      new THREE.CircleGeometry(9, 48),
      new THREE.MeshLambertMaterial({ color: COLORS.water })
    );
    sea.rotation.x = -Math.PI / 2;
    sea.position.y = -0.16;
    sea.receiveShadow = true;
    this.world.add(sea);

    this.world.add(buildCountry(this.compact));
    this.world.add(buildBorder());

    this.addMarkers();
  }

  addMarkers() {
    this.cities.forEach((city) => {
      const colour = new THREE.Color(city.color || COLORS.marker);
      const marker = buildMarker(colour);
      marker.position.set(city.x * SCALE, 0.14, city.z * SCALE);
      marker.userData.city = city;
      marker.userData.baseColor = colour;
      marker.userData.phase = Math.random() * Math.PI * 2;
      this.world.add(marker);
      this.markers.push(marker);

      // Names are given away in teaser mode only — the quiz has to be a quiz.
      if (this.mode === 'teaser') {
        const label = buildLabel(city.name);
        label.position.set(city.x * SCALE, 0.78, city.z * SCALE);
        marker.userData.label = label;
        this.world.add(label);
      }
    });
  }

  bind() {
    const canvas = this.renderer.domElement;

    this.onPointerMove = (event) => {
      const rect = canvas.getBoundingClientRect();
      this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      this.targetSpin = this.pointer.x * (this.mode === 'quiz' ? 0.16 : 0.3);
    };

    this.onPointerLeave = () => {
      this.pointer.set(-2, -2);
      this.targetSpin = 0;
    };

    this.onClick = (event) => {
      if (this.locked) return;
      const rect = canvas.getBoundingClientRect();
      this.pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      this.pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      const hit = this.pick();
      if (!hit) return;

      const slug = hit.userData.city.slug;
      if (this.mode === 'quiz') {
        this.container.dispatchEvent(
          new CustomEvent('map:guess', { detail: { slug }, bubbles: true })
        );
      } else {
        this.highlight(slug);
        this.container.dispatchEvent(
          new CustomEvent('map:select', { detail: { slug }, bubbles: true })
        );
      }
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
    };
    window.addEventListener('resize', this.onResize);

    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => (entry.isIntersecting ? this.start() : this.stop()));
    }, { threshold: 0.01 });
    this.observer.observe(this.container);

    this.onVisibility = () => (document.hidden ? this.stop() : this.start());
    document.addEventListener('visibilitychange', this.onVisibility);
  }

  pick() {
    this.raycaster.setFromCamera(this.pointer, this.camera);
    const hits = this.raycaster.intersectObjects(this.markers, true);
    if (!hits.length) return null;
    let object = hits[0].object;
    while (object && !object.userData.city) object = object.parent;
    return object;
  }

  markerFor(slug) {
    return this.markers.find((marker) => marker.userData.city.slug === slug);
  }

  paint(marker, colour) {
    marker.userData.painted.forEach((mesh) => mesh.material.color.set(colour));
  }

  /** Teaser mode: raise one marker and dim the rest. */
  highlight(slug) {
    this.markers.forEach((marker) => {
      const isActive = marker.userData.city.slug === slug;
      marker.userData.active = isActive;
      this.paint(marker, isActive ? COLORS.active : marker.userData.baseColor);
      if (marker.userData.label) marker.userData.label.material.opacity = isActive ? 1 : 0.55;
    });
  }

  /** Quiz mode: flash the answer, then settle back to neutral. */
  reveal({ guessed, correct }) {
    this.locked = true;

    const correctMarker = this.markerFor(correct);
    const guessedMarker = guessed ? this.markerFor(guessed) : null;

    if (guessedMarker && guessed !== correct) {
      this.paint(guessedMarker, COLORS.wrong);
      guessedMarker.userData.shake = 1;
    }
    if (correctMarker) {
      this.paint(correctMarker, COLORS.correct);
      correctMarker.userData.active = true;
      if (!correctMarker.userData.label) {
        const label = buildLabel(correctMarker.userData.city.name);
        label.position.set(
          correctMarker.position.x, 0.82, correctMarker.position.z
        );
        correctMarker.userData.label = label;
        correctMarker.userData.temporaryLabel = true;
        this.world.add(label);
      }
    }
  }

  /** Clear the previous question's colours and labels. */
  resetRound() {
    this.locked = false;
    this.markers.forEach((marker) => {
      marker.userData.active = false;
      marker.userData.shake = 0;
      this.paint(marker, marker.userData.baseColor);
      if (marker.userData.temporaryLabel && marker.userData.label) {
        this.world.remove(marker.userData.label);
        marker.userData.label.material.map?.dispose();
        marker.userData.label.material.dispose();
        marker.userData.label = null;
        marker.userData.temporaryLabel = false;
      }
    });
  }

  animate = () => {
    if (!this.running) return;
    this.frame = requestAnimationFrame(this.animate);
    const elapsed = this.clock.getElapsedTime();

    const drift = this.mode === 'teaser' ? Math.sin(elapsed * 0.12) * 0.12 : 0;
    this.spin += (this.targetSpin + drift - this.spin) * 0.06;
    this.world.rotation.y = this.spin;

    const hovered = this.locked ? null : this.pick();
    this.renderer.domElement.style.cursor = hovered ? 'pointer' : 'default';

    this.markers.forEach((marker) => {
      const lifted = marker.userData.active || marker === hovered;
      const targetY = lifted ? 0.32 : 0.14;
      marker.position.y += (targetY - marker.position.y) * 0.15;

      // A brief wobble on a wrong answer.
      if (marker.userData.shake > 0) {
        marker.userData.shake = Math.max(0, marker.userData.shake - 0.02);
        marker.rotation.z = Math.sin(elapsed * 38) * 0.22 * marker.userData.shake;
      } else if (marker.rotation.z !== 0) {
        marker.rotation.z = 0;
      }

      const halo = marker.userData.halo;
      if (halo) {
        const pulse = 1 + Math.sin(elapsed * 2 + marker.userData.phase) * 0.12;
        halo.scale.setScalar(lifted ? pulse * 1.4 : pulse);
        halo.material.opacity = lifted ? 0.62 : 0.32;
      }

      if (marker.userData.label) {
        marker.userData.label.position.y = marker.position.y + 0.62;
      }
    });

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
      const materials = Array.isArray(object.material) ? object.material : [object.material];
      materials.forEach((material) => {
        material?.map?.dispose();
        material?.dispose();
      });
    });
    this.renderer.dispose();
    this.renderer.domElement.remove();
  }
}

export function initGermanyMap(container) {
  if (prefersReducedMotion()) return null;

  let cities = [];
  try {
    cities = JSON.parse(container.dataset.cities || '[]');
  } catch {
    cities = [];
  }
  if (!cities.length) return null;

  const fallback = container.querySelector('[data-map-fallback]');
  if (fallback) fallback.hidden = true;

  return new GermanyMap(container, cities, { mode: container.dataset.mode || 'teaser' });
}

export default initGermanyMap;
