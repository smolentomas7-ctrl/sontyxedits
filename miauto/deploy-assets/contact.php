<?php
/**
 * Enquiry form handler for traditional (Apache + PHP) hosting.
 *
 * The site is a static export. On Netlify the form posts to Netlify Forms,
 * which does not exist on this host, so this script takes its place: it is the
 * only server-side code in the deployment and it does exactly one thing.
 *
 * It answers JSON. The front end treats a 200 whose body is not {"ok":true} as
 * a failure and shows the error state with the phone number, so a message is
 * never reported as sent unless mail() accepted it for delivery.
 *
 * Configure the two constants below. Nothing here needs an API key.
 */

declare(strict_types=1);

// ── configuration ──────────────────────────────────────────────────────────

/** Where enquiries are delivered. */
const MAIL_TO = 'ivanautoservisrk@gmail.com';

/**
 * The envelope sender. It MUST be a mailbox on this site's own domain, or the
 * receiving server sees mail claiming to be from a domain this server is not
 * allowed to send for and files it as spam. A Gmail address here is the single
 * most common reason enquiries disappear — do not put MAIL_TO in this field.
 */
const MAIL_FROM = 'web@autoservisruzomberoksro.sk';

/** Minimum seconds between two submissions from one address. */
const THROTTLE_SECONDS = 20;

// ── plumbing ───────────────────────────────────────────────────────────────

header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');

/** Answer and stop. The body is the whole contract with the front end. */
function reply(int $status, bool $ok, string $error = ''): never {
    http_response_code($status);
    echo json_encode($ok ? ['ok' => true] : ['ok' => false, 'error' => $error]);
    exit;
}

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    reply(405, false, 'method');
}

/** Trimmed POST field, with a hard length cap so nothing unbounded is accepted. */
function field(string $name, int $max): string {
    $value = $_POST[$name] ?? '';
    if (!is_string($value)) {
        return '';
    }
    return mb_substr(trim($value), 0, $max);
}

// ── spam checks, cheapest first ────────────────────────────────────────────

// The honeypot is hidden from people and filled in by bots. Answer as though it
// worked: a bot told it failed simply tries again differently.
if (field('bot-field', 100) !== '') {
    reply(200, true);
}

// The throttle is checked here but only RECORDED after a message is actually
// sent. Recording it now would mean a visitor who mistypes their phone number
// and corrects it two seconds later is told to wait, which punishes the person
// filling the form in properly rather than the machine hammering it.
$ip = (string) ($_SERVER['REMOTE_ADDR'] ?? '');
$stamp = $ip !== '' ? sys_get_temp_dir() . '/miauto-' . hash('sha256', $ip) . '.throttle' : '';
if ($stamp !== '') {
    $last = @filemtime($stamp);
    if ($last !== false && (time() - $last) < THROTTLE_SECONDS) {
        reply(429, false, 'throttled');
    }
}

// ── validation, repeated here because the browser's copy can be bypassed ───

$name    = field('meno', 80);
$phone   = field('telefon', 40);
$email   = field('email', 120);
$vehicle = field('vozidlo', 120);
$service = field('sluzba', 80);
$message = field('sprava', 4000);
$consent = field('suhlas', 10);

if (mb_strlen($name) < 2)                          reply(422, false, 'name');
if (preg_match('/^[+0-9\s().\/-]+$/', $phone) !== 1) reply(422, false, 'phone');
$digits = preg_replace('/\D/', '', $phone) ?? '';
if (mb_strlen($digits) < 9 || mb_strlen($digits) > 15) reply(422, false, 'phone');
if ($email !== '' && !filter_var($email, FILTER_VALIDATE_EMAIL)) reply(422, false, 'email');
if (mb_strlen($message) < 10)                      reply(422, false, 'message');
if ($consent === '')                               reply(422, false, 'consent');

// A newline in a header field is how a header injection starts. These values
// are the only ones that reach a header, so they are the only ones to clean.
$headerSafe = static fn (string $v): string => str_replace(["\r", "\n"], ' ', $v);

// ── compose and send ───────────────────────────────────────────────────────

$subject = '=?UTF-8?B?' . base64_encode('Dopyt z webu — ' . $name) . '?=';

$body = implode("\n", [
    'Meno:    ' . $name,
    'Telefón: ' . $phone,
    'E-mail:  ' . ($email !== '' ? $email : '(neuvedený)'),
    'Vozidlo: ' . ($vehicle !== '' ? $vehicle : '(neuvedené)'),
    'Služba:  ' . $service,
    '',
    'Správa:',
    $message,
    '',
    '--',
    'Odoslané z kontaktného formulára na ' . ($_SERVER['HTTP_HOST'] ?? 'webe') . '.',
]);

$headers = [
    'MIME-Version: 1.0',
    'Content-Type: text/plain; charset=UTF-8',
    'Content-Transfer-Encoding: 8bit',
    'From: =?UTF-8?B?' . base64_encode('Web — M.I.Auto') . '?= <' . MAIL_FROM . '>',
];
// Reply-To only when the customer gave an address, so hitting reply writes back
// to them rather than to the website's own mailbox.
if ($email !== '') {
    $headers[] = 'Reply-To: ' . $headerSafe($email);
}

$sent = @mail(MAIL_TO, $subject, $body, implode("\r\n", $headers), '-f' . MAIL_FROM);

// Deliberately not logged: the message, the name, the phone number, the email.
// A failure says that it failed and nothing about who wrote it.
if (!$sent) {
    error_log('miauto contact form: mail() refused the message');
    reply(502, false, 'send');
}

// Sent. Now the clock starts.
if ($stamp !== '') {
    @touch($stamp);
}

reply(200, true);
