import axios, { AxiosResponse } from 'axios';
import { useState } from 'react';

enum EStatus {
    DONE = 'd',
    IN_PROGRESS = 'i',
    SUBMITTED = 's',
    ERROR = 'e',
}

interface ICurrentJob {
    id: number | null;
    url: string;
}

interface IResult {
    created_at: string;
    updated_at: string;
    id: number;
    url: string;
    status: EStatus;
    result: {
        links: {
            url: string;
            links: string[];
            error?: string;
        }[];
        error?: string;
    };
}

const isValidHttpUrl = (str: string) => {
    let url;

    try {
        url = new URL(str);
    } catch (_) {
        return false;
    }

    return url.protocol === 'http:' || url.protocol === 'https:';
};

const createJob = async (url: string) => {
    try {
        const res = await axios.post<{ url: string }, AxiosResponse<{ created: string; job_id: number }>>(
            'http://localhost:8080/api/parse/',
            { url }
        );
        return res.data;
    } catch (err) {
        alert(`ОШИБКА: ${JSON.stringify(err, null, 2)}`);
    }
};

let ACTUAL_JOB_ID = {};

const poolJob = async (currentJobId: object, job_id: number, delay = 2000, max = 1000 * 60 * 60 * 3) => {
    const sleep = (ms: number) => {
        return new Promise<void>(res => {
            setTimeout(() => res(), ms);
        });
    };

    while (max) {
        if (ACTUAL_JOB_ID !== currentJobId) {
            // Outdated request. Do nothing.
            return null;
        }
        try {
            const res = await axios.get<{jobs: IResult[]}>(`http://localhost:8080/api/jobs/${job_id}/`);
            console.log('@@@', res)
            if (![EStatus.DONE, EStatus.ERROR].includes(res.data.jobs[0]?.status)) {
                await sleep(delay);
                max -= delay;
                continue;
            } else {
                return res.data.jobs[0] ?? null;
            }
        } catch (err) {
            alert(`ОШИБКА: ${JSON.stringify(err, null, 2)}`);
            return null;
        }
    }
};

export default function Main(props: Record<string, never>) {
    const [urlValue, setUrlValue] = useState<string>('');
    const [urlError, setUrlError] = useState<string>('Please enter a URL');
    const [touched, setTouched] = useState<boolean>(false);
    const [currentJob, setCurrentJob] = useState<ICurrentJob | null>(null);
    const [result, setResult] = useState<null | IResult>(null);

    const notFinished = result == null || [EStatus.IN_PROGRESS, EStatus.SUBMITTED].includes(result.status);
    const done = result?.status === EStatus.DONE;

    return (
        <fieldset>
            <legend>Crawler</legend>
            <p>
                <label htmlFor="url-input">URL</label>
                <br />
                <input
                    id="url-input"
                    type="url"
                    placeholder="Enter a URL here"
                    onChange={event => {
                        setTouched(false);
                        const val = event.target.value;
                        if (!val || !isValidHttpUrl(val)) {
                            setUrlError('Please enter a valid URL');
                            setUrlValue('');
                        } else {
                            setUrlError('');
                            setUrlValue(val);
                        }
                    }}
                />
                {urlError && touched && <>{urlError}</>}
            </p>
            <p>
                <button
                    type="button"
                    name="button"
                    onClick={event => {
                        setTouched(true);
                        if (!urlError && urlValue && currentJob?.url !== urlValue) {
                            const currentJobId = {};
                            ACTUAL_JOB_ID = currentJobId;
                            setCurrentJob({ url: urlValue, id: null });
                            setResult(null);
                            console.log('@@@0')
                            createJob(urlValue).then(res => {
                                if (ACTUAL_JOB_ID !== currentJobId) {
                                    // Outdated request. Do nothing.
                                    return;
                                }
                                setCurrentJob({
                                    url: urlValue,
                                    id: res?.job_id ?? null,
                                });
                                console.log('@@@1', res)
                                if (res?.job_id) {
                                    console.log('@@@2')
                                    poolJob(currentJobId, res?.job_id).then(data => {
                                        console.log('@@@3', data?.result)
                                        if (data != null) {
                                            setResult(data);
                                        }
                                    });
                                }
                            });
                        }
                    }}
                >
                    Go
                </button>
            </p>
            {currentJob !== null && notFinished && (
                <>
                    <hr />
                    <strong>{currentJob.url} hyperlinks:</strong>
                    <p>
                        <div className="lds-dual-ring"></div>
                    </p>
                </>
            )}
            {currentJob !== null && done && (
                <>
                    <hr />
                    <strong>{urlValue}</strong>
                    <pre id='pre-block'>
                        {result.result.error && `ОШИБКА: ${result.result.error}`}
                        <ol>
                            {result.result.links.map(el => (
                                <li>
                                    {el.url}
                                    {el.error && `ОШИБКА: ${el.error}`}
                                    <ol>
                                        {el.links.map(href => (
                                            <li>{href}</li>
                                        ))}
                                    </ol>
                                </li>
                            ))}
                        </ol>
                    </pre>
                </>
            )}
        </fieldset>
    );
}
